// Obtener referencias
const btnEasterEgg = document.getElementById("btnEasterEgg");
const easterModal = document.getElementById("easterModal");
const closeEasterEgg = document.getElementById("closeEasterEgg");

btnEasterEgg.addEventListener("click", () => {
  easterModal.classList.remove("hidden");
  btnEasterEgg.style.display = "none";
});

closeEasterEgg.addEventListener("click", () => {
  easterModal.classList.add("hidden");
  btnEasterEgg.style.display = "block";
});

function filtrarSucursales() {
  const input = document.getElementById("buscadorSucursal").value.toLowerCase();
  const sucursales = document.querySelectorAll(".sucursal-item");

  sucursales.forEach((item) => {
    const nombre = item.getAttribute("data-nombre");
    if (nombre.includes(input)) {
      item.style.display = "flex";
    } else {
      item.style.display = "none";
    }
  });
}

function getPrecioSucursal(nombre) {
    const precios = {
        "Sucursal 1": 333,
        "Sucursal 2": 222,
        "Sucursal 3": 1111
    };
    return precios[nombre] || 0;
}


function calcular() {
    const cantidadInput = document.getElementById("cantidad").value;
    const sucursal = document.getElementById("selectSucursal").value;
    const cantidad = parseInt(cantidadInput);

    if (!cantidad || cantidad <= 0) {
        alert("Por favor, ingresa una cantidad válida.");
        return;
    }

    const precio = getPrecioSucursal(sucursal);
    const total_clp = precio * cantidad;

    fetch("/calcular_usd", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ total_clp: total_clp })
    })
    .then(res => res.json())
    .then(data => {
        const resultado = `Total CLP: $${total_clp.toLocaleString("es-CL")} | Total USD: $${data.total_usd}`;
        document.getElementById("resultados").innerText = resultado;

        // Habilitar botón de pagar
        const pagarBtn = document.getElementById("btnPagar");
        if (pagarBtn) {
            pagarBtn.onclick = () => iniciarPago(total_clp);
            pagarBtn.disabled = false;
        }
    })
    .catch(() => alert("Error al calcular el total en USD."));
}

function iniciarPago(monto) {
    const sucursal = document.getElementById("selectSucursal").value;
    const cantidad = parseInt(document.getElementById("cantidad").value);

    fetch("/iniciar_pago", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ amount: monto, sucursal: sucursal, cantidad: cantidad })
    })
    .then(response => response.json())
    .then(data => {
        if (data.url && data.token) {
            const form = document.createElement("form");
            form.method = "POST";
            form.action = data.url;

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "token_ws";
            input.value = data.token;

            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        } else {
            alert("Error al iniciar el pago.");
        }
    })
    .catch(error => {
        console.error("Error en el pago:", error);
        alert("Hubo un problema al conectar con el servidor.");
    });
}
