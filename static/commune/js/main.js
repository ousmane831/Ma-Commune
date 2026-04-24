(function () {
  var btn = document.getElementById("btn-copy-link");
  if (btn && navigator.clipboard && btn.dataset.url) {
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(btn.dataset.url).then(function () {
        btn.textContent = "Copié !";
        setTimeout(function () {
          btn.textContent = "Copier le lien";
        }, 2000);
      });
    });
  }
})();
