import re
import shutil


from static.py import imareocr, sqlite_core
from static.py.cam_service import camera
from flask_socketio import SocketIO
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

PASTA = r"X:\OPERACOES\13-ALMOXARIFADO\0 - Sistema Almox"

app = Flask(__name__)
Socket = SocketIO(app, async_mode='eventlet')

sqlite = sqlite_core.init(PASTA)

tools_db = sqlite_core.init.tools(sqlite)
mails_db = sqlite_core.init.mails(sqlite)

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

with app.app_context():
    print("✅ Servidor iniciado com sucesso!")
    
@app.route("/")
def fallback():
    return render_template("mails/mails.html")

@app.route("/tool-loans/")
@app.route("/tool-loans/<subpath>")
def tool_loans(subpath = None):
    if subpath is None or subpath != "registers":
        return render_template("tool-loans/check-out.html")
    else:  
        return render_template("tool-loans/registers.html")

@app.route("/mails")
def mails():
    return render_template("mails/mails.html")

@app.route("/tool-loans/add-tool", methods=["POST"])
def add_tool():
    data = request.json
    
    if data == None:
        return jsonify({"Message": "Error: Código invalido!"}, 404)

    if not (item := tools_db.searchTools(data.get("code"))):
        return jsonify({"Message": "Error: Código não encontrado!"}, 404)
    
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

@app.route("/pictures/<path:filename>")
def picture(filename):
    return send_from_directory(PASTA + r"\pictures", filename)

@app.route("/get-registers", methods=["GET"])
def get_registers():
    print(f"{datetime.now()} | {request.remote_addr} Getting tools")
    
    return jsonify({
        "loaned_tools": tools_db.getAllLoanedItems(),
        "all_movements": tools_db.getAllMovements()
    }, 200)
    
@app.route("/tool-loans/registers/missing", methods=["POST"])
def missing():
    data = request.json
    if data:
        tools_db.setToolMissing(data.get("code"))
            
    return jsonify({
        "Message": "Ok"
    }, 200)

@Socket.on("update_pictures")
def update_pictures():
    Socket.emit("update_pictures")
    
    
    
    

@app.route("/user-ip", methods=["GET"])
def getIp():
    return jsonify({
        "Message": request.remote_addr
    }, 200)





@app.route("/mails/get-mails", methods=["POST"])
def get_mails():
    data = request.get_json()

    print(f"{datetime.now()} | {request.remote_addr} Getting Mails - Data: {data[0], data[1]}")

    return jsonify({
        "mails": mails_db.getMails(data[0], data[1])
    }, 200)
    
    
@app.route("/mails/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({
            "Message": "Error: Nenhum arquivo enviado!"
        }, 400)
    
    file = request.files["file"]
    
    tmp_path = PASTA + r"\pictures\mails\temp_image.jpg"
    
    file.save(tmp_path)
        
    print(f"{datetime.now()} | {request.remote_addr} file uploaded - '{tmp_path}'")
    
    global lastImage
    lastImage = tmp_path
    
    texto_extraido = imareocr.extractText(tmp_path)
    
    return jsonify(texto_extraido)
    
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

            dest_path = f"pictures/mails/{pname}.jpg"

            shutil.copy(lastImage, dest_path)
            
            mails_db.updatePicture(
                motivo,
                date,
                pname,
                code,
                "returned"
            )

            inserted.append(code)

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

    dest_path = f"pictures/mails/{pname}.jpg"
    shutil.move(lastImage, dest_path)

    mails_db.updatePicture(user, date, pname, code, "shipped")

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
            return jsonify({
                "Message": "Registro efetuado com Sucesso!"
            }, 200)
    else:
        return jsonify({
            "Message": "Código de rastreio invalido!"
        }, 422)

@app.route("/mails/received", methods=["POST"])
def received():
    data = request.get_json()

    code = data["code"]
    receiver = data["receiver"]
    sender = data["sender"]
    
    if re.match(r'^[A-Za-z]{2}\d{9}BR$', str(code).upper()):
        filteredMails = mails_db.getMails(str(code), 'id')
        filteredMails = filteredMails[0]
        if (filteredMails[6] == None or filteredMails[7] == None):
            mails_db.updateReceiver(str(code), str(receiver), str(sender))
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
            "Message": "Código de rastreio invalido!"
        }, 422)



if __name__ == "__main__":
    Socket.run(app, host="0.0.0.0", port=80)