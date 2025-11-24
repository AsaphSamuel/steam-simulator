document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const errorMsg = document.getElementById("login-error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorMsg.style.display = "none";

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    console.log("Usuário:", username);
    console.log("Senha:", password);

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (data.success) {
        window.location.href = "/home";
      } else {
        errorMsg.textContent = data.message || "Usuário ou senha incorretos.";
        errorMsg.style.display = "block";
      }
    } catch (err) {
      errorMsg.textContent = "Erro de conexão com o servidor.";
      errorMsg.style.display = "block";
      console.error("Erro:", err);
    }
  });
});
