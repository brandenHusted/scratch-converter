// functions
function goodString(string) {
  let convertedString = string.toLowerCase();
  convertedString = convertedString.replace(/\s+/g, '_');

  return convertedString;
}

// global variables
let fileName = "";


// file upload
const fileInput = $("#file");
const label = fileInput.prev();

fileInput.on("change", function(e) {
  if (this.files && this.files.length > 1) {
    fileName = (this.getAttribute("data-multiple-caption") || "").replace(
      "{count}",
      this.files.length
    );
  } else {
    fileName = e.target.value.split("\\").pop();
  }
  if (fileName) {
    label.html(fileName);
  } else {
    label.html("Select file");
  }
});

// generate
let generateBtn = document.querySelector(".generate");
generateBtn.addEventListener("click", e => {
  if (fileInput[0].files.length == 0) {
    e.preventDefault();
    alert("Please select a file first!!!!");
    return;
  }
  $(".bg").show();
  generateBtn.nextElementSibling.click()
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
