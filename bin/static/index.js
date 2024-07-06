const progressbar = document.querySelector(".progress");
const block_settings = document.querySelector('.settings form');

window.onload = function () {
  try {
    new QWebChannel(qt.webChannelTransport, function (channel) {
      window.PyHandler = channel.objects.PyHandler;
    });
  } catch (e) {
    window.console.log(e)
  }
  setTimeout(function () {
    window.PyHandler.load_data()
  }, 250);
}

// rewrite this
window.add_item = function (msg, fsize) {
  let div = document.createElement('div');
  div.className = 'item';

  let filename = document.createElement('div');
  filename.className = 'filename';
  filename.textContent = msg;
  filename.title = msg;

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
    window.PyHandler.download(msg);
  };

  let itemsDiv = document.querySelector('.items');
  itemsDiv.appendChild(div);
}
// ###

function clear_filters(folder) {
  const folderElement = document.querySelector('.folders');
  if (folderElement.querySelector('.folder.active')) {
    folderElement.querySelector('.folder.active').classList.remove('active');
  }
  folder.classList.add('active');
  window.PyHandler.start_page();
}
function add_folder(name) {
  const folderElement = document.querySelector('.folders');
  let newFolder = document.createElement('div');
  newFolder.className = 'folder';
  newFolder.textContent = name;
  newFolder.addEventListener('click', () => {
    if (folderElement.querySelector('.folder.active')) {
      folderElement.querySelector('.folder.active').classList.remove('active');
    }
    newFolder.classList.add('active');
    window.PyHandler.filtered_page(name)
  });
  folderElement.appendChild(newFolder);
}
window.add_filters = function(filters_array) {
  var folders = document.querySelector('.folders');
  var elements = folders.querySelectorAll('.folder');
  if (elements.length >= 3) {
    for (var i = 2; i < elements.length; i++) {
      folders.removeChild(elements[i]);
    }
  }
  filters_array.forEach((folder) => {
    add_folder(folder);
  });
}

const changeProgress = (progress) => {
  progressbar.style.width = `${progress}%`;
};


let popupBg = document.querySelector('.popup__bg');
let popup = document.querySelector('.popup');

const ul = document.querySelector("ul");
const input = document.querySelector("input");

let maxTags = 10;
let tags = [];

function createTag() {
  ul.querySelectorAll("li").forEach(li => li.remove());
  tags.slice().reverse().forEach(tag => {
    let liTag = `<li onclick="remove(this, '${tag}')">${tag}</li>`;
    ul.insertAdjacentHTML("afterbegin", liTag);
  });
}
function remove(element, tag) {
  let index = tags.indexOf(tag);
  tags = [...tags.slice(0, index), ...tags.slice(index + 1)];
  element.remove();
}
function addTag(e) {
  if (e.key == "Enter") {
    let tag = e.target.value.replace(/\s+/g, ' ');
    if (tag.length > 1 && !tags.includes(tag)) {
      if (tags.length < 10) {
        tag.split(',').forEach(tag => {
          tags.push(tag);
          createTag();
        });
      }
    }
    e.target.value = "";
  }
}
input.addEventListener("keyup", addTag);

function popup_menu_creator(e) {
  let filename = e.getElementsByClassName('filename')[0];
  let filename_text = filename.innerText;

  var popup_filename = popup.querySelector('.popup_filename');
  popup_filename.textContent = filename_text

  var delete_file = popup.querySelector('.delete.fold');
  delete_file.onclick = function() {
    window.PyHandler.del_item(filename_text)
    popupBg.classList.remove('active');
    popup.classList.remove('active');
  }

  window.PyHandler.popup_get_filters(filename_text)
}

document.addEventListener('mousedown', (e) => {
  if (e.target.parentElement.className == 'item' && e.button == 2) {
    e.preventDefault();
    popupBg.classList.add('active');
    popup.classList.add('active');

    popup_menu_creator(e.target.parentElement)

  }
})

document.addEventListener('click', (e) => {
  if (e.target === popupBg) {
    popupBg.classList.remove('active');
    popup.classList.remove('active');

    var popup_filename = popup.querySelector('.popup_filename');
    window.PyHandler.popup_set_filters(popup_filename.innerText, tags)
  }
});

function show_hide_settings() {
  var blockSettings = document.querySelector('.settings');

  if (blockSettings.classList.contains('hide')) {
    blockSettings.classList.remove('hide');
    blockSettings.style.animation = 'slideFromBottom 0.5s forwards';

    window.PyHandler.get_bots()
  } else {
    blockSettings.style.animation = 'slideFromBottom 0.5s reverse';
    blockSettings.classList.add('hide');

    window.PyHandler.set_bots(bots)
  }
}


var bots = []

function createBots() {
  block_settings.innerHTML = '';
  bots.slice().forEach(bot => {

    block_settings.appendChild(addBotLine(bot.id, bot.token, bot.chat_id))
  });
}

function update_token(id, token) {
  for (let i = 0; i < bots.length; i++) {
    if (bots[i].id == id) {
      bots[i].token = token;
      break;
    }
  }
}

function update_id(id, chat_id) {
  for (let i = 0; i < bots.length; i++) {
    if (bots[i].id == id) {
      bots[i].chat_id = chat_id;
      break;
    }
  }
}


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

  var deleteButton = document.createElement('div');
  deleteButton.title = 'Remove';
  deleteButton.innerHTML = "<img src='static\\icons\\delete.svg' />";
  deleteButton.addEventListener('click', (event) => remove_bot(id));


  chat_inputContainer.appendChild(chat_inputElement);
  chat_inputContainer.appendChild(underline);
  chat_inputContainer.appendChild(chat_labelElement);

  bot_inputContainer.appendChild(bot_inputElement);
  bot_inputContainer.appendChild(underline);
  bot_inputContainer.appendChild(bot_labelElement);


  container.appendChild(deleteButton);
  container.appendChild(bot_inputContainer);
  container.appendChild(chat_inputContainer);


  return container;
}
function remove_bot(id) {
  window.PyHandler.remove_bot(id)
}


function toggleNotification() {
  let element = document.getElementById('notification');
  if (element.classList.contains('hidden')) {
    element.classList.remove('hidden');
  } else {
    element.classList.add('hidden');
  }
}
function setText(text) {
  let element = document.getElementById('notification');
  let child = element.children[0];
  child.textContent = text;
}