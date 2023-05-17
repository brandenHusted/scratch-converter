// functions
function goodString(string) {
  let convertedString = string.toLowerCase();
  convertedString = convertedString.replace(/\s+/g, "_");

  return convertedString;
}

// global variables
let fileName = "";
let goodFileName = "";

// editor
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");
editor.setReadOnly(true);

// step 1

// file upload
const fileInput = $("#file");
const label = fileInput.prev();

fileInput.on("change", function (e) {
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
    goodFileName = goodString(fileName);
    console.log(goodFileName);
  } else {
    label.html("Select file");
  }
});

// generate event
let fakeGBtn = $("#generateBtn");
let realGBtn = fakeGBtn.next();
fakeGBtn.on("click", (e) => {
  if (fileInput[0].files.length == 0) {
    e.preventDefault();
    alert("Please select a file first!!!!");
    return;
  }
  $(".bg").show();
  realGBtn.click();
});

// show preview btn
function showOrClosePreview(btn) {
  let right = $(".main > .right");
  if (right.is(":visible")) {
    btn.html("Show Preview");
    right.animate({ width: 0 }, 500, function () {
      $(this).hide();
    });
    return;
  }
  btn.html("Close Preview");
  // it's flex, so 100% only shows 50%
  right.show().animate({ width: "100%" }, 500);
}

let previewBtn = $(".show-preview");
previewBtn.on("click", () => showOrClosePreview(previewBtn));

// download
$(".download").click(function () {
  let downloadBtn = $(this);
  location.href = "/download/" + downloadBtn.attr("data-key");
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
