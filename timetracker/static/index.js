// Functions to timer in home page
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
let startWatch;
let time = 0;
let timeInterval;

const formatTime = (time) => {
    let diffH = time / 3600000;
    let hours = Math.floor(diffH);
    hours = hours < 10 ? `0${hours}` : hours;

    let diffM = (diffH - hours) * 60;
    let minutes = Math.floor(diffM);
    minutes = minutes < 10 ? `0${minutes}` : minutes;

    let diffS = (diffM - minutes) * 60;
    let seconds = Math.floor(diffS);
    seconds = seconds < 10 ? `0${seconds}` : seconds;

    let diffMs = (diffS - seconds) * 100;
    let milliseconds = Math.floor(diffMs);
    milliseconds = milliseconds < 10 ? `0${milliseconds}` : milliseconds;

    return `${hours}:${minutes}:${seconds}:${milliseconds}`;
}

const show = (text) => {
    document.getElementById('watch').innerHTML = text;
}

const start = () => {
    startWatch = Date.now() - time;
    timeInterval = setInterval(function showTime() {
        time = Date.now() - startWatch;
        show(formatTime(time));
    }, 10);
    startBtn.style.display = "none";
    pauseBtn.style.display = "inline-block";
}

const pause = () => {
    clearInterval(timeInterval);
    startBtn.style.display = "inline-block";
    pauseBtn.style.display = "none";
}

const reset = () => {
    clearInterval(timeInterval);
    show('00:00:00:00')
    time = 0;
    startBtn.style.display = "inline-block";
    pauseBtn.style.display = "none";
}

// Function that copy time from timer
const clipboardCopy = () => {
  let text = document.querySelector("#watch").textContent.split(":");
  let first = Math.floor(text[0]);
  let second = Math.floor((text[1] / 60) * 100);
  second = second < 10 ? `0${second}` : second;

  navigator.clipboard.writeText(`${first}.${second}`);
}
document.getElementById('copyBtn').addEventListener('click', clipboardCopy);