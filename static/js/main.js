/////////////////////////////////////////////////////////
////////              Functions                    ////////
/////////////////////////////////////////////////////////
function goodString(string) {
  let convertedString = string.toLowerCase();
  convertedString = convertedString.replace(/\s+/g, "_");
  convertedString = convertedString.replace(/\.sb3$/, "");
  return convertedString;
}

function renderTextBox(data) {
  const {msg, out, err} = data;

  const outLines = out.split("\n");
  const errLines = out.split("\n");
  $(".text-box").append(`<p>${msg}</p>`);
  for (let i = 0; i < outLines.length; i++) {
    $(".text-box").append(`<p>${outLines[i]}</p>`);
  }
  for (let i = 0; i < errLines.length; i++) {
    $(".text-box").append(`<p>${errLines[i]}</p>`);
  }
}

/////////////////////////////////////////////////////////
////////              Global Variables              ////////
/////////////////////////////////////////////////////////
let fileName = "";
let goodFileName = "";
let link = "";
let key = "";

/////////////////////////////////////////////////////////
////////                  Editor                   ////////
/////////////////////////////////////////////////////////
const renderEditor = code => {
  $(".right").empty();
  $(".right").append('<div id="editor"></div>');
  $("#editor").html(code);
  const editor = ace.edit("editor");
  editor.setTheme("ace/theme/monokai");
  editor.session.setMode("ace/mode/python");
  editor.setReadOnly(true);
};

/////////////////////////////////////////////////////////
////////                  Steps                    ////////
/////////////////////////////////////////////////////////
const step1 = $(".step1");
const step2_1 = $(".step2.link");
const step2_2 = $(".step2.file");
const step3 = $(".step3");
const step4 = $(".step4");
let jumpThrough = "";

/////////////////////////////////////////////////////////
////////                  Step1                    ////////
/////////////////////////////////////////////////////////
const throughLink = $(".step1 .link");
const throughFile = $(".step1 .file");
throughLink.on("click", () => {
  step1.hide();
  step2_1.show();
});
throughFile.on("click", () => {
  step1.hide();
  step2_2.show();
});

/////////////////////////////////////////////////////////
////////                  Step2                   ////////
/////////////////////////////////////////////////////////
const backToStep1 = $(".step2 .back");
backToStep1.on("click", () => {
  step2_1.hide();
  step2_2.hide();
  step1.show();
});

const nextToStep3 = $(".step2 .next");
nextToStep3.on("click", function () {
  step2_1.hide();
  step2_2.hide();
  console.log($(this));
  if ($(this).hasClass("link_")) {
    jumpThrough = "link";
  } else if ($(this).hasClass("file_")) {
    jumpThrough = "file";
  }
  step3.show();
});

// if input, show next btn
const linkInput = $("#link");
const fileInput = $("#file");
const fileInputLabel = fileInput.prev();
step2_1.find(".next").hide();
step2_2.find(".next").hide();

// make sure link is valid
// should start with https://scratch.mit.edu/projects/
function validLink(link) {
  let regex = /^https:\/\/scratch.mit.edu\/projects\/.*?/;
  return regex.test(link);
}

linkInput.on("input", function () {
  if (this.value && validLink(this.value)) {
    link = this.value;
    step2_1.find(".next").show();
  } else {
    step2_1.find(".next").hide();
  }
});

fileInput.on("change", function () {
  if (this.files.length > 0) {
    step2_2.find(".next").show();
  } else {
    step2_2.find(".next").hide();
  }
});

// file select
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
    fileInputLabel.html(fileName);
    $("#file_name").html(fileName);
    goodFileName = goodString(fileName);
  } else {
    fileInputLabel.html("Select file");
  }
});

/////////////////////////////////////////////////////////
////////                  Step3                   ////////
/////////////////////////////////////////////////////////
const backToStep2 = $(".step3 .back");
backToStep2.on("click", () => {
  step3.hide();
  if (jumpThrough == "link") {
    step2_1.show();
  } else if (jumpThrough == "file") {
    step2_2.show();
  }
});

const nextToStep4 = $(".step3 .next");
nextToStep4.hide();
nextToStep4.on("click", () => {
  step3.hide();
  step4.show();
});

// dynamic lang
let lang = $("#lang");
let langSelector = $("#language");
lang.text(langSelector.val());
langSelector.on("change", () => {
  lang.text(langSelector.val());
});

// generate
const generateBtn = $(".step3 .generate");
generateBtn.on("click", () => {
  $(".bg").show();
  nextToStep4.show();
  if (jumpThrough == "link") {
    $.ajax({
      url: "/generate/link",
      method: "POST",
      data: JSON.stringify({ link: link, lang: langSelector.val() }),
      contentType: "application/json",
      success: function (data) {
        $(".bg").hide();
        console.log(data);
        if (data.code === 1) {
          key = data.key;
          renderTextBox(data);
          renderEditor(data.python_code);
          step3.hide();
          step4.show();
        }
      },
      error: function (err) {
        $(".bg").hide();
        console.log(err);
      },
    });
  } else if (jumpThrough == "file") {
    let formData = new FormData();
    formData.append("fileName", goodFileName);
    formData.append("file", fileInput[0].files[0]);
    formData.append("lang", langSelector.val());
    $.ajax({
      url: "/generate/file",
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (data) {
        $(".bg").hide();
        console.log(data);
        if (data.code === 1) {
          key = data.key;
          renderTextBox(data);
          renderEditor(data.python_code);
          step3.hide();
          step4.show();
        }
      },
      error: function (err) {
        $(".bg").hide();
        console.log(err);
      },
    });
  }
});

/////////////////////////////////////////////////////////
////////                  Step4                   ////////
/////////////////////////////////////////////////////////
const backToStep3 = $(".step4 .back");
backToStep3.on("click", () => {
  step4.hide();
  step3.show();
  $(".right").hide();
  $(".show-preview").html("Show Preview");
});

const backToStart = $(".step4 .next");
backToStart.on("click", () => {
  step4.hide();
  step1.show();
  $(".right").hide();
  $(".show-preview").html("Show Preview");
})

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
  location.href = "/download/" + key;
});
