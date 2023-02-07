
// Title functions

function showHelpWindowTitle() {
    document.getElementById("help-window-title").style.display = "block";
}

function closeHelpWindowTitle() {
    document.getElementById("help-window-title").style.display = "none";
}

function generateSongTitle() {
    const xhr = new XMLHttpRequest();
    const song_name = "";
    const ending_words = "";
    const keywords = "";
    const uniqueness = document.getElementById("uniqueness").value;
    const rhyme = "";
    const add_emotion = "";
    const emotion = "";
    const sentence = "";
    xhr.open("GET", "/generate_title?song_name=" + song_name + "&line_num=0" +
        "&ending_words=" + ending_words + "&keywords=" + keywords + "&uniqueness=" + uniqueness +
        "&rhyme=" + rhyme + "&add_emotion=" + add_emotion + "&emotion=" + emotion + "&sentence=" + sentence,
        true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById("title-text").value = xhr.responseText;
        }
    };
    xhr.send();
}

// Text Functions

function showHelpWindow(i) {
    document.getElementById("song-text-" + i).removeAttribute("disabled");
    document.getElementById("help-window-" + i).style.display = "block";
}

function closeHelpWindow(i) {
    document.getElementById("help-window-" + i).style.display = "none";
    document.getElementById("song-text-" + i).setAttribute("disabled", "disabled");
    for (let j = 0; j < 100; j++) {
        document.getElementById("song-text-" + j).setAttribute("disabled", "disabled");
        if (document.getElementById("main-div-" + (j+1)).style.display === "none") {
            document.getElementById("song-text-" + j).removeAttribute("disabled");
            document.getElementById("main-div-" + j).style.display = "block";
            break;
        }
    }
}

function generateSongText(i) {
    const xhr = new XMLHttpRequest();
    const song_name = "";
    const ending_words = document.getElementById("ending-words-input").value;
    const keywords = document.getElementById("line-key-words-input").value;
    const uniqueness = document.getElementById("uniqueness").value;
    const rhyme = document.getElementById("rhyme").checked;
    const add_emotion = document.getElementById("emotion-check").checked;
    const emotion = document.getElementById("emotion").value;
    xhr.open("GET", "/generate?song_name=" + song_name + "&line_num=" + i +
        "&ending_words=" + ending_words + "&keywords=" + keywords + "&uniqueness=" + uniqueness +
        "&rhyme=" + rhyme + "&add_emotion=" + add_emotion + "&emotion=" + emotion + "&sentence=", true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById("song-text-" + i).value = xhr.responseText;
        }
    };
    xhr.send();
}

function completeSongText(i) {
    const xhr = new XMLHttpRequest();
    const song_name = "";
    const ending_words = document.getElementById("ending-words-input").value;
    const keywords = document.getElementById("line-key-words-input").value;
    const uniqueness = document.getElementById("uniqueness").value;
    const rhyme = document.getElementById("rhyme").checked;
    const add_emotion = document.getElementById("emotion-check").checked;
    const emotion = document.getElementById("emotion").value;
    const sentence = document.getElementById("song-text-" + i).value
    xhr.open("GET", "/complete?song_name=" + song_name + "&line_num=" + i +
        "&ending_words=" + ending_words + "&keywords=" + keywords + "&uniqueness=" + uniqueness +
        "&rhyme=" + rhyme + "&add_emotion=" + add_emotion + "&emotion=" + emotion + "&sentence=" + sentence,
        true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById("song-text-" + i).value = xhr.responseText;
        }
    };
    xhr.send();
}

function rephraseSongText(i) {
    const xhr = new XMLHttpRequest();
    const song_name = "";
    const ending_words = document.getElementById("ending-words-input").value;
    const keywords = document.getElementById("line-key-words-input").value;
    const uniqueness = document.getElementById("uniqueness").value;
    const rhyme = document.getElementById("rhyme").checked;
    const add_emotion = document.getElementById("emotion-check").checked;
    const emotion = document.getElementById("emotion").value;
    const sentence = document.getElementById("song-text-" + i).value
    xhr.open("GET", "/rephrase?song_name=" + song_name + "&line_num=" + i +
        "&ending_words=" + ending_words + "&keywords=" + keywords + "&uniqueness=" + uniqueness +
        "&rhyme=" + rhyme + "&add_emotion=" + add_emotion + "&emotion=" + emotion + "&sentence=" + sentence,
        true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById("song-text-" + i).value = xhr.responseText;
        }
    };
    xhr.send();
}