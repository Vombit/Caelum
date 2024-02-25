const progressbar = document.querySelector(".progress");
const popup = document.getElementById('popup');

window.onload = function () {
  try {
    new QWebChannel(qt.webChannelTransport, function (channel) {
      window.PyHandler = channel.objects.PyHandler;
    });
  } catch (e) {
    window.console.log(e)
  }
  setTimeout(function () {
    window.PyHandler.load()
  }, 500);
}

window.add_item = function (msg, fsize) {
  let div = document.createElement('div');
  div.className = 'item';

  let filename = document.createElement('div');
  filename.className = 'filename';
  filename.textContent = msg;

  let download = document.createElement('div');
  download.className = 'btn_download noselect';
  download.textContent = 'download';

  let size = document.createElement('div');
  size.className = 'file_size noselect';
  size.textContent = '~'+fsize+'GB';

  div.appendChild(filename);
  div.appendChild(size);
  div.appendChild(download);

  download.onclick = function() {
    window.PyHandler.downloader(msg);
  };

  let itemsDiv = document.querySelector('.items');
  itemsDiv.appendChild(div);
}
function update_token(arg) {
  window.PyHandler.settings_token(arg)
}
function update_id(arg) {
  window.PyHandler.settings_id(arg)
}
function show_hide_settings() {
  var block_settings = document.querySelector('.settings');
  
  if (block_settings.style.display === "none") {
    block_settings.style.display = "flex";
  }else {
    block_settings.style.display = "none";
  }
}

const changeProgress = (progress) => {
  progressbar.style.width = `${progress}%`;
};

function openPopup(text) {
  var popupContent = document.querySelector('.popup-content');
  popupContent.innerHTML = text;
  popup.style.display = 'block';
}

function closePopup() {
  document.getElementById('popup').style.display = 'none';
}