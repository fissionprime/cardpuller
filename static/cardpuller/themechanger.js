(function () {
  /* bind an event listener to all elements with class '.theme-toggle' that
toggles between dark and light mode on click. Any checkbox elements will also
have their "checked" element updated to match the current theme
IMPORTANT: before loading this script the vars dark_url and light_url must be
defined as the paths to the dark and light theme css files, respectively*/
  var win = window;
  var doc = win.document;
  var storage = localStorage;

  var pref_key = "preferred_theme";
  var pref = storage.getItem(pref_key);

  // we use these strings alot so we will define them for convenience
  var dark = "dark";
  var light = "light";

  var default_theme = light;
  var theme_toggles = doc.querySelectorAll(".theme-toggle");
  var theme_source = doc.querySelector("#current-theme");

  // we will use this to track if dark mode is currently on
  var dark_active = (default_theme === dark);

  // again, dark_url and light_url must be defined before loading this script
  function changeTheme(theme) {
    if (theme === dark) theme_source.setAttribute('href', dark_url);
    else theme_source.setAttribute('href', light_url);
    dark_active = (theme === dark);
  }

  var update_checkboxes = function (bool) {
    for (toggle of theme_toggles) {
        if (bool) toggle.checked = true;
        else toggle.checked = false;
    }
      
  };
  // load any preferences in localStorage
  if (pref === dark) changeTheme(dark);
  if (pref === light) changeTheme(light);
  
  // no preference in localStorage
  if (!pref) {
    var prefers = function(theme) {
        return '(prefers-color-scheme: ' + theme + ')';
    };

    // check for OS preferences for the theme
    if (win.matchMedia(prefers(dark)).matches) changeTheme(dark);
    else if (win.matchMedia(prefers(light)).matches) changeTheme(light);
    else changeTheme(default_theme);
  }

  // make sure that the document contains toggles
  if (theme_toggles[0]) {
    for (toggle of theme_toggles) {
      toggle.addEventListener('click', function () {
        if (dark_active) {
          changeTheme(light);
          storage.setItem(pref_key, light);
          // Update any checkbox elements
          update_checkboxes(false);
        }
        else {
          changeTheme(dark);
          storage.setItem(pref_key, dark);
          update_checkboxes(true);
        }
      }, true);
    }
  }
})();