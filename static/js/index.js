function update() {
    window.started_show = true;
    this.form.submit();
    console.log("change");
  }
document.getElementById("uploadInput").addEventListener("change", update, false);