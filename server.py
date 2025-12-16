import re
import shutil
import webbrowser

from flask_socketio import SocketIO
from static.py.cam_service import camera
from static.py import imareocr, sqlite_core
from flask import Flask, request, jsonify, render_template, send_from_directory



# ################################ #
#      Initializing Essencial      #
#             Modules              #
# ################################ # 



FOLDER = r"\\192.168.7.252\dados\OPERACOES\13-ALMOXARIFADO\0 - Sistema Almox"

imgReader = imareocr.init(FOLDER)
sqlite = sqlite_core.init(FOLDER)

tools_db = sqlite_core.init.tools(sqlite)
mails_db = sqlite_core.init.mails(sqlite)


app = Flask(__name__)

Socket = SocketIO(
    app, 
    async_mode="eventlet"
)

# ################################ #
#          Setting Global          #
#            Variables             #
# ################################ # 



lastImage = ""

meses = {
    "01": "jan",
    "02": "fev",
    "03": "mar",
    "04": "abr",
    "05": "mai",
    "06": "jun",
    "07": "jul",
    "08": "ago",
    "09": "set",
    "10": "out",
    "11": "nov",
    "12": "dez"
}



# ################################ #
#          Defining Main           #
#              Routes              #
# ################################ # 



with app.app_context():
    print("Servidor iniciado com sucesso!")
    webbrowser.open("http://192.168.7.20")

@app.route("/")
def fallback():
    return render_template("mails/mails.html")

@app.route("/tools-loan/")
@app.route("/tools-loan/<subpath>")
def tool_loans(subpath = None):
    if subpath is None or subpath != "registers":
        return render_template("tools-loan/check-out.html")
    else:  
        return render_template("tools-loan/registers.html")

@app.route("/mails")
def mails():
    return render_template("mails/mails.html")

@app.route("/user-ip", methods=["GET"])
def getIp():
    return jsonify({
        "Message": request.remote_addr
    }, 200)

@app.route("/pictures/<path:filename>")
def picture(filename):
    return send_from_directory(FOLDER + r"\pictures", filename)

# ################################ #
#          Routes to the           #
#          Tools-loan Tab          #
# ################################ # 



@app.route("/tools-loan/add-tool", methods=["POST"])
def add_tool():
    data = request.json
    
    if data == None:
        return jsonify({
            "Message": "Error: Código invalido!"
        }, 404)

    if not (item := tools_db.searchTools(data.get("code"))):
        return jsonify({
            "Message": "Error: Código não encontrado!"
        }, 404)
    
    if item[3].lower() == "disponivel":
        type = "saida"
        status = "Emprestado"
    elif item[3].lower() == "emprestado":
        type = "entrada"
        status = "Disponivel"
    
    movements_count = tools_db.getMovementsCount()
    
    photo = camera.capture(str(movements_count).zfill(6))
    
    tools_db.updateTools(item[0], "status", status)
    
    movement = tools_db.addMovement(
        movements_count, 
        item[0], 
        photo["day"], 
        photo["month"], 
        photo["year"], 
        photo["time"], 
        type
    )
    
    tools_db.updateTools(item[0], "id_movements", movement[0])

    return jsonify({
        "item": item, 
        "movement": movement,
        "photo": photo
    }, 200)

@app.route("/tools-loan/get-registers", methods=["GET"])
def get_registers():
    
    return jsonify({
        "loaned_tools": tools_db.getAllLoanedItems(),
        "all_movements": tools_db.getAllMovements()
    }, 200)
    
@app.route("/tools-loan/registers/missing", methods=["POST"])
def missing():
    data = request.json
    if data:
        tools_db.setToolMissing(data.get("code"))
            
    return jsonify({
        "Message": "Ok"
    }, 200)



# ################################ #
#          Routes to the           #
#            mails Tab             # 
# ################################ # 



@app.route("/mails/get-mails", methods=["POST"])
def get_mails():
    data = request.get_json()

    return jsonify({
        "mails": mails_db.getMails(data[0], data[1])
    }, 200)
    
    
@app.route("/mails/upload_file", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({
                "Message": "Error: Nenhum arquivo enviado!"
            }, 400)
        
        file = request.files["file"]
        
        tmp_path = FOLDER + r"\pictures\mails\temp_image.jpg"
        
        file.save(tmp_path)
        
        global lastImage

        sqlite.log_edit(
            entity="/mails/upload_file",
            entity_id="File",
            field=None,
            old=lastImage,
            new=tmp_path,
            ip=request.remote_addr
        )

        lastImage = tmp_path
        
        texto_extraido = imgReader.extractText(tmp_path)
    
        return jsonify(texto_extraido)
    except Exception as e:
        sqlite.log_edit(
            entity="/mails/upload_file",
            entity_id=None,
            field="Error",
            old=None,
            new=e,
            ip=request.remote_addr
        )
        return jsonify(":(")
    
@app.route("/mails/update", methods=["POST"])
def update():
    data = request.get_json()

    mail_type = data.get("type")
    date = data.get("date")

    if mail_type == "return":
        items = data.get("items", [])

        if not items:
            return jsonify({
                "Message": "Nenhuma devolução informada"
            }, 400)

        inserted = []

        for item in items:
            code = item.get("code")
            motivo = item.get("motivo")

            if not code:
                continue

            infos = mails_db.getMails(code, "id")
            
            if not infos:
                continue

            infos = infos[0]

            pname = (
                str(infos[4][:3].upper()) +
                str(infos[2][-5:]) +
                str(infos[0])
            )

            dest_path = FOLDER + r"\pictures\mails\\" + pname + ".jpg"

            shutil.copy(lastImage, dest_path)
            
            mails_db.updatePicture(
                motivo,
                date,
                pname,
                code,
                "returned"
            )

            inserted.append(code)

            sqlite.log_edit(
                entity="/mails/update",
                entity_id=code,
                field="status",
                old=None,
                new="returned",
                ip=request.remote_addr
            )
            
        return jsonify({
            "Message": "Devoluções registradas",
            "type": "returns"
        }, 200)
    
    code = data.get("code")
    user = data.get("user")

    if not code or not user:
        return jsonify({
            "Message": "Dados inválidos"
        }, 400)

    infos = mails_db.getMails(code, "id")

    if not infos:
        return jsonify({
            "Message": "Correspondência não encontrada"
        }, 404)

    infos = infos[0]

    pname = (
        str(infos[4][:3].upper()) +
        str(infos[2][-5:]) +
        str(infos[0])
    )

    dest_path = FOLDER + r"\pictures\mails\\" + pname + ".jpg"
    
    shutil.move(lastImage, dest_path)

    mails_db.updatePicture(user, date, pname, code, "shipped")

    sqlite.log_edit(
        entity="/mails/update",
        entity_id=code,
        field="status",
        old=None,
        new="shipped",
        ip=request.remote_addr
    )
    
    return jsonify({
        "Message": "Entrega registrada",
        "PictureName": pname
    }, 200)
    

@app.route("/mails/register", methods=["POST"])
def register():
    data = request.get_json()

    code = data["code"]
    name = data["name"]
    fantasy = data["fantasy"]
    type_ = data["type"]
    status = data["status"]
    priority = data["priority"]
    
    if re.match(r'^[A-Za-z]{2}\d{9}BR$', str(code).upper()):
        if ("unique constraint failed" in str(mails_db.register(str(name), str(code), str(fantasy), str(type_), str(priority), str(status))).lower()):
            return jsonify({
                "Message": "Essa correspondencia ja está cadastrada!"
            }, 409)
        else:
            sqlite.log_edit(
                entity="/mails/register",
                entity_id=code,
                field=None,
                old=None,
                new=None,
                ip=request.remote_addr
            )

            return jsonify({
                "Message": "Registro efetuado com Sucesso!"
            }, 200)
    else:
        return jsonify({
            "Message": "Código de rastreio invalido!"
        }, 409)

@app.route("/mails/update-reception-received", methods=["POST"])
def reception_received():
    data = request.get_json()

    code = data["code"]
    receiver = data["receiver"]
    sender = data["sender"]
    
    if re.match(r'^[A-Za-z]{2}\d{9}BR$', str(code).upper()):
        filteredMails = mails_db.getMails(str(code), 'id')
        if filteredMails:
            filteredMails = filteredMails[0]
            if (filteredMails[6] == None or filteredMails[7] == None):
                mails_db.updateReceiver(str(code), str(receiver), str(sender))

                sqlite.log_edit(
                    entity="/mails/update-reception-received",
                    entity_id=code,
                    field=None,
                    old=receiver,
                    new=sender,
                    ip=request.remote_addr
                )
                return jsonify({
                    "Message": "Status atualizado com sucesso!"
                }, 200)
            else:
                return jsonify({
                    "Message": "A correspondencia ja foi coletada!",
                    "Values": [f"Recebedor: {filteredMails[6].title()}" , f"Liberador: {filteredMails[7].title()}"]
                }, 409)
        else:
            return jsonify({
                "Message": "Correspondencia não encontrada!"
            }, 404)
    else:
        return jsonify({
            "Message": "Código de rastreio invalido!"
        }, 422)

@app.route("/mails/change-fantasy-name", methods=["POST"])
def change_fantasy():
    data = request.get_json()

    code = data.get("code")
    new_value = data.get("new_value")
    old_value = data.get("old_value")

    mails_db.updateFantasy(str(code), str(new_value))

    sqlite.log_edit(
        entity="/mails/change-fantasy-name",
        entity_id=code,
        field="fantasy",
        old=old_value,
        new=new_value,
        ip=request.remote_addr
    )

    return jsonify({
        "Message": "Nome atualizado com sucesso!"
    }, 200)


# ################################ #
#             SocketIO             #
#              Repass              #
# ################################ # 



@Socket.on("update_pictures")
def update_pictures():
    Socket.emit("update_pictures")




if __name__ == "__main__":
    Socket.run(app, host="0.0.0.0", port=80)