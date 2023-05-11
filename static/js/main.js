// file upload
let fileInput = document.getElementById("file");
let label = fileInput.previousElementSibling;

fileInput.addEventListener("change", function (e) {
  let fileName = "";
  if (this.files && this.files.length > 1) {
    fileName = (this.getAttribute("data-multiple-caption") || "").replace(
      "{count}",
      this.files.length
    );
  } else {
    fileName = e.target.value.split("\\").pop();
  }
  if (fileName) {
    label.innerHTML = fileName;
  } else {
    label.innerHTML = "Select file";
  }
});

// generate
let generateBtn = document.querySelector(".generate");
generateBtn.addEventListener("click", e => {
  if (fileInput.files.length == 0) {
    e.preventDefault();
    alert("Please select a file first!!!!");
    return;
  }
});

// show preview btn
function showOrClosePreview(btn) {
  let right = document.querySelector(".main > .right");
  if (right.style.display === "block") {
    btn.innerHTML = "Show Preview";
    right.style.display = "none";
    return;
  }
  btn.innerHTML = "Close Preview";
  right.style.display = "block";
}

let previewBtn = document.querySelector(".show-preview");
previewBtn.addEventListener("click", () => showOrClosePreview(previewBtn));

// download
let downloadBtn = document.querySelector(".download");
downloadBtn.addEventListener("click", () => {
  location.href = "/download/" + downloadBtn.getAttribute("data-key");
});

// after generated
function afterGenerated() {
  let btns = document.querySelector(".btns");
  if (btns.getAttribute("data-show") == "1") {
    btns.style.display = "flex";
  }
}

afterGenerated();

// dynamic lang
let lang = document.querySelector("#lang");
let langSelector = document.querySelector("#language");
lang.innerHTML = langSelector.value;
langSelector.addEventListener("change", () => {
  lang.innerHTML = langSelector.value;
});
