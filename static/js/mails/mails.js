let last_filter = ""
let last_orderBy = "id"

function changeShipContainer(event) {
    document.querySelectorAll(".ship-container").forEach(container => {
        container.style.display = "none";
    });

    if(event.target.checked) {
        document.getElementById("ship-almox").style.display = "grid";
    } else {
        document.getElementById("ship-mall").style.display = "grid";
    }
}

function getCorrespondences(filter, orderBy) {
    if (last_orderBy != orderBy && orderBy) {
        last_orderBy = orderBy
    }

    if (filter !== "" && filter !== null) {
        last_filter = filter
    } else if(filter === "") {
        last_filter = null
    }

    fetch("/mails/get-mails", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify([last_filter, last_orderBy])
    })
    .then(response => response.json())
    .then(json => {
        const container = document.getElementById("db-container");

        document.querySelectorAll('.db-container-values, .db-container-title')
            .forEach(el => el.remove());

        container.innerHTML += `
            <div class="db-container-title">
                <b id="id">ID</b>
                <b id="name">Nome</b>
                <b id="code">Codigo AR</b>
                <b id="fantasy">Nome Fantasia</b>
                <b id="type">Tipo</b>
                <b id="priority">Prioridade</b>
                <b id="join_date">Data Entrada</b>
                <b id="receive_name">Quem Recebeu</b>
                <b id="receive_date">Data Recebimento</b>
                <b id="photo_id">Comprovante</b>
            </div>
        `
        const headers = document.querySelectorAll(".db-container-title b");

        headers.forEach(header => {
            header.classList.remove("order")
            header.addEventListener("click", () => {
                const orderByButton = header.id;
                getCorrespondences(null, orderByButton);
            });
        });

        document.getElementById(last_orderBy).classList.add("order")
        document.getElementById("search_input").value = last_filter ? last_filter : ""

        const content_container = document.createElement("div");

        content_container.classList.add("db-container-values")

        Object.entries(json[0].mails).forEach(data => {
            Object.entries(data[1]).forEach((correpondence, index, array) => {
                if (index !== 6 && index !== 7 && index !== 8) {
                    if (index === array.length - 1) {
                        const td = document.createElement("td");
                        td.classList.add("picture_link");
                        
                        td.textContent = correpondence[1];
                        td.dataset.img = data[1][12] ? `/pictures/mails/${data[1][12]}.jpg` : "";
                        
                        if (data[1][8] == "on_reception") {
                            td.classList.add("on_reception")
                        } else if (data[1][8] == "returned") {
                            td.classList.add("returned")
                        }

                        content_container.appendChild(td);

                        td.addEventListener("click", function () {
                            window.open(td.dataset.img, "_blank");
                        })

                    } else {
                        const field = document.createElement("td");
                        if (data[1][8] == "on_reception") {
                            field.classList.add("on_reception")
                        } else if (data[1][8] == "returned") {
                            field.classList.add("returned")
                        }

                        field.textContent = correpondence[1];
                        content_container.appendChild(field);
                    }
                }
            });
        });
        
        container.appendChild(content_container);
    })
}


function updateReceiver() {
    const input = document.getElementById("file_input");

    document.querySelector(".to_almox").style.display = "none"

    const formData = new FormData();
    formData.append("file", input.files[0]);
    
    const img_container = document.getElementById("image-container")
    const ur_button = document.getElementById("updateReceiver-button")

    if(input.files[0]) {
        ur_button.disabled = true
        document.getElementById("file_input").disabled = true

        img_container.classList.add("loading");
    }   

    fetch("/mails/upload_file", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(json => {
        const regexCodigo = /([A-Z]{2}\d{9}[A-Z]{2})/;
        const codigoMatch = json.replaceAll(" ", "").toUpperCase().match(regexCodigo);
        const codigo = codigoMatch ? codigoMatch[1] : null;

        const regexRecebido = /R[E3][CÇ][E3][B8][I1l][D0O][O0]?\s*P[O0]R\s*:\s*([^\n\r]+)/;
        const recebidoMatch = json.replaceAll(" ", "").toUpperCase().match(regexRecebido);
        const recebido = recebidoMatch ? recebidoMatch[1] : null;
        
        const regexData = /DATA:\s*([0-9Iil\/]{6,12})/i;
        const dataMatch = json.match(regexData);

        let data = null

        if (dataMatch) {
            let raw = dataMatch[1];

            raw = raw.replace(/[^0-9]/g, "");

            const day = raw.slice(0, 2);
            const month = raw.slice(2, 4);
            const year = raw.slice(4, 8);

            data = `${year}-${month}-${day}`
        }


        if (data == null || isNaN(new Date(data).getTime())) {
            const today = new Date();
            const dd = String(today.getDate()).padStart(2, '0');
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const yyyy = today.getFullYear();

            data = `${dd}-${mm}-${yyyy}`;
        }

        img_container.classList.add("pp-small")
        img_container.classList.remove("loading")
        img_container.addEventListener("click", function () {
            window.open(document.getElementById("picture-preview").src)
        })

        ur_button.remove()
        
        const container = document.getElementById("ship-container");
        
        const body = document.createElement("div")
        body.classList.add("sc-body")

        const code_input = document.createElement("input")
        const user_input = document.createElement("input")
        const data_input = document.createElement("input")
                        
        const submit = document.createElement("button")
        
        submit.type = "submit"
        submit.classList.add("submit")
        submit.innerHTML = "Registrar"

        code_input.value = codigo
        code_input.id = "code_input"

        user_input.value = recebido
        user_input.id = "user_input"

        data_input.type = "date"
        data_input.value = data
        data_input.id = "data_input"


        body.appendChild(code_input)
        body.appendChild(user_input)
        body.appendChild(data_input)
        body.appendChild(submit)

        container.appendChild(body)
        
        submit.addEventListener("click", () => {
            const [day, month, year] = data_input.value.split("-");

            fetch("/mails/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify([code_input.value, user_input.value, `${year}-${month}-${day}`])
            })
            .then(response => response.json())
            .then(data => {
                if(data[1] == 200) {
                    focuses("db-container")
                    getCorrespondences(data[0].PictureName)

                    setTimeout(() => document.querySelectorAll(".db-container-values td").forEach(b => b.classList.add("highlight")), 100)
                } else if(data[1] == 404) {
                    document.getElementById("code_input").classList.add("not_found")

                    let errorMsg = document.getElementById("error_message")

                    if (errorMsg) {
                        errorMsg.innerText = data[0].Error
                    } else {
                        const h1 = document.createElement("h1")
                        h1.id = "error_message"
                        h1.innerHTML = data[0].Error
                        body.appendChild(h1)
                    }
                }
            })
        })
    });
}

let actual_focus = "insert-container"

function focuses(container) {
    document.querySelectorAll(".container").forEach(container => {
        container.style.display = "none";
    });
    document.getElementById(container).style.display = "grid";
    actual_focus = String(container)

    if(container == "ship-container") {
        const img_container = document.getElementById("image-container")

        img_container.addEventListener("click", () => {
            const file_input = document.getElementById("file_input")
            file_input.click()
            file_input.addEventListener("change", () => {
                const file = file_input.files[0]
                if (file) {
                    img_container.innerHTML = `
                        <img id="picture-preview" class="picture-preview" src="${URL.createObjectURL(file)}" alt="image">
                    `
                }
            })
        })

    }
}

function register() {
    const form = document.getElementById("insert-container");

    if (!form.reportValidity()) {
        return;
    }

    const code = document.getElementById("ar_code")
    const name = document.getElementById("mail_name")
    const fantasy = document.getElementById("mail_fantasy")
    const type = document.getElementById("mail_type")
    const status = document.getElementById("mail_status")
    const priority = document.getElementById("mail_priority")

    const payload = {
        code: code.value,
        name: name.value,
        fantasy: fantasy.value,
        type: type.value,
        status: status.value,
        priority: priority.value
    };

    fetch("/mails/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {

        document.getElementById("insert-message").innerHTML = data[0].Message;
        switch (data[1]) {
            case 200:
                code.value = ""
                name.value = ""
                fantasy.value = ""
                break
            case 404:
            case 422:
            case 409:
                code.classList.add("not_found")
                break
            default:
                document.getElementById("insert-message").innerHTML = "Occorreu um erro não esperado!"
        }
            
    })


    // if (response.status === 200) {
    //     setTimeout(() => location.reload(), 900);
    // }
}

function receivedOnReception() {
    const form = document.getElementById("ship-almox");

    if (!form.reportValidity()) {
        return;
    }

    const code = document.getElementById("mail_code")
    const receiver = document.getElementById("receiver_name")
    const sender = document.getElementById("sender_name")

    const payload = {
        code: code.value,
        receiver: receiver.value,
        sender: sender.value
    };

    fetch("/mails/received", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        messageh1 = document.getElementById("reception-insert-message")
        messageh1.innerHTML = data[0].Message;

        switch (data[1]) {
            case 200:
                code.value = ""
                break
            case 404:
            case 422:
                code.classList.add("not_found")
                break
            case 409:
                code.classList.add("not_found")
                messageh1.innerHTML += `
                    <br>
                    <br>
                    ${data[0].Values[0]}
                    <br>
                    ${data[0].Values[1]}
                `
                break
            default:
                document.getElementById("reception-insert-message").innerHTML = "Occorreu um erro não esperado!"
        }
    })
}




document.addEventListener("keydown", function (event) {
    if (event.key == " " && event.target.id == "ar_code") {
        event.preventDefault();
    }

    if ((event.target.id == "code_input" || event.target.id == "ar_code" || event.target.id == "mail_code") && "not_found" == event.target.classList[0]) {
        event.target.classList.remove("not_found")
        
        if (actual_focus === "ship-container") {
            document.getElementById("error_message").innerText = ""
        } else if (actual_focus === "insert-container") {
            document.getElementById("insert-message").innerText = "Preencha os campos a baixo!"
        } else if (actual_focus === "reception-container") {
            document.getElementById("reception-insert-message").innerText = "Preencha os campos a baixo!"
        }
    }

    function openSelect(el) {
        if (!el) return;
        if (typeof el.showPicker === "function") {
            try {
                el.focus();
                el.showPicker();
                return;
            } catch (e) {
                // continua para fallback
            }
        }

        try {
            el.focus();
            el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
            el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
            el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        } catch (e) {
            console.warn("openSelect fallback falhou:", e);
        }
    }

    if (event.key === 'Tab' || event.key === 'Enter') { event.preventDefault(); }

    if ((event.key === 'Enter' || event.key === "Tab") && actual_focus === "insert-container") {
        const inputs = ["ar_code", "mail_name", "mail_fantasy", "mail_type", "mail_priority", "mail_status", "submit"];

        const activeElement = document.activeElement;
        const currentIndex = inputs.indexOf(activeElement.id);

        const nextIndex = (currentIndex + 1) % inputs.length;
        const prevIndex = (currentIndex - 1 + inputs.length) % inputs.length; // evita negativo

        if (event.shiftKey) {
            const target = document.getElementById(inputs[prevIndex]);
            if (prevIndex <= 2) {
                target && target.select();
            } else if (prevIndex === 3 || prevIndex === 4 || prevIndex === 5) {
                openSelect(target);
            } else {
                target && target.focus();
            }
            return;
        }

        const target = document.getElementById(inputs[nextIndex]);
        if (nextIndex <= 2) {
            target && (target.focus(), target.select());
        } else if (nextIndex === 3 || nextIndex === 4 || nextIndex === 5) {
            openSelect(target);
        } else if (nextIndex === 6) {
            target && target.focus();
        }

        if (
            (currentIndex == 5 && event.key === 'Enter') ||
            ((currentIndex == 3 || currentIndex == 4) &&
             (event.key === 'Enter' || event.key === 'Tab'))
        ) {
            document.getElementById(inputs[currentIndex])?.click();
        }
    } else if (actual_focus === "db-container") {
        const inputs = ["search_input", "search_button"];

        const activeElement = document.activeElement;
        const currentIndex = inputs.indexOf(activeElement.id);

        const nextIndex = (currentIndex + 1) % inputs.length;
        const prevIndex = (currentIndex - 1 + inputs.length) % inputs.length;


        if (event.shiftKey) {
            const target = document.getElementById(inputs[prevIndex]);
            target.focus()
            return;
        } else if(event.key === 'Tab') {
            const target = document.getElementById(inputs[nextIndex]);
            target.focus();
        } else if(event.target.id != "search_input") {
            const target = document.getElementById(inputs[0]);
            target.focus();
        }

        if (currentIndex == 0 && event.key === 'Enter') {
            document.getElementById(inputs[nextIndex])?.click();
            setTimeout(() => 
                document.getElementById(inputs[currentIndex]).focus()
            , 200)
        }
    } else if ((event.key === 'Enter' || event.key === "Tab") && actual_focus === "ship-container") {
        const inputs = ["mail_code", "receiver_name", "sender_name", "reception-submit"];

        const activeElement = document.activeElement;
        const currentIndex = inputs.indexOf(activeElement.id);

        const nextIndex = (currentIndex + 1) % inputs.length;
        const prevIndex = (currentIndex - 1 + inputs.length) % inputs.length;

        if (event.shiftKey) {
            const target = document.getElementById(inputs[prevIndex]);
            if (prevIndex <= 0) {
                target && target.select();
            } else if (prevIndex === 1 || prevIndex === 2) {
                openSelect(target);
            } else {
                target && target.focus();
            }
            return;
        }

        const target = document.getElementById(inputs[nextIndex]);
        if (nextIndex === 0) {
            target && target.select();
        } else if (nextIndex === 2 || nextIndex === 1) {
            openSelect(target);
        } else {
            target && target.focus();
        }

        if (currentIndex == 3 && event.key === 'Enter') {
            document.getElementById(inputs[currentIndex])?.click();
        }
    }
});

const preview = document.createElement("img");
preview.className = "picture_preview";
document.body.appendChild(preview);

document.addEventListener("mousemove", function(e) {
    if (preview.style.display === "block") {
        preview.style.left = (e.pageX - 360) + "px";
        preview.style.top  = (e.pageY - 180) + "px";
    }
});

document.addEventListener("mouseover", function(e) {
    if (e.target.classList.contains("picture_link") && e.target.getAttribute("data-img")) {
        const img = e.target.getAttribute("data-img");
        preview.src = img;
        preview.style.display = "block";
    }
});

document.addEventListener("mouseout", function(e) {
    if (e.target.classList.contains("picture_link")) {
        preview.style.display = "none";
    }
});