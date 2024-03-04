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
function update_token(id, arg) {
  window.PyHandler.settings_token(id, arg)
}
function update_id(id, arg) {
  window.PyHandler.settings_id(id, arg)
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


function context_menu_creator(e) {
  var context = document.createElement('div');
  var filenameElement = e.target.parentElement.getElementsByClassName('filename')[0];
  context.id = "context_menu";
  console.log(filenameElement)
  context.innerHTML = `
      <div onclick="window.PyHandler.del_item('${filenameElement.innerText}')">delete</div>
      `;
  context.style.top = e.y + 'px';
  context.style.left = e.x + 'px';
  document.getElementsByTagName("body")[0].appendChild(context);
}

document.addEventListener("contextmenu", function(e) {
  if (e.target.parentElement.className == 'item') {
      if (!document.getElementById("context_menu")) {
          context_menu_creator(e)
      } else {
          document.getElementById("context_menu").remove();
          context_menu_creator(e)
      }
  }
  window.event.returnValue = false;
}, false);
document.addEventListener("click", function(e) {
  if (e.target.id != "context_menu" && document.getElementById("context_menu")) {
      document.getElementById("context_menu").remove();
  }
});

function addBotLine(id=null, bot_token=null, chat_token=null) {
  var container = document.createElement('div');
  container.className = 'form-row';

  var bot_inputContainer = document.createElement('div');
  bot_inputContainer.className = 'input-data';
  var bot_labelElement = document.createElement('label');
  bot_labelElement.className = 'noselect';
  bot_labelElement.textContent = 'Bot token';
  var bot_inputElement = document.createElement('input');
  bot_inputElement.type = 'text';
  bot_inputElement.required = true;
  bot_inputElement.id = id;
  bot_inputElement.setAttribute('value', bot_token);
  bot_inputElement.addEventListener('change', (event) => update_token(event.target.id, event.target.value));

  var underline = document.createElement('div');
  underline.className = 'underline';

  var chat_inputContainer = document.createElement('div');
  chat_inputContainer.className = 'input-data';
  var chat_labelElement = document.createElement('label');
  chat_labelElement.className = 'noselect';
  chat_labelElement.textContent = 'Chat id';
  var chat_inputElement = document.createElement('input');
  chat_inputElement.type = 'text';
  chat_inputElement.required = true;
  chat_inputElement.id = id;
  chat_inputElement.setAttribute('value', chat_token);
  chat_inputElement.addEventListener('change', (event) => update_id(event.target.id, event.target.value));


  chat_inputContainer.appendChild(chat_inputElement);
  chat_inputContainer.appendChild(underline);
  chat_inputContainer.appendChild(chat_labelElement);

  bot_inputContainer.appendChild(bot_inputElement);
  bot_inputContainer.appendChild(underline);
  bot_inputContainer.appendChild(bot_labelElement);

  container.appendChild(bot_inputContainer);
  container.appendChild(chat_inputContainer);

  return container;
}

var block_settings = document.querySelector('.settings form');