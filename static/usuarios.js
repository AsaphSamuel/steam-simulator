async function carregarTentativas() {
    const resposta = await fetch("/api/tentativas");
    const dados = await resposta.json();

    let html = "<h2>Registros encontrados:</h2><ul>";

    dados.forEach(item => {
        html += `<li>${JSON.stringify(item)}</li>`;
    });

    html += "</ul>";

    document.getElementById("resultado").innerHTML = html;
}
