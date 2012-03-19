// Namespaces
tinymce = {}
tinymce.dom = {}
tinymce.html = {}
tinymce.ui = {}
tinymce.util = {}
tinymce.plugins = {}

// Classes
tinymce.AddOnManager = function() {
	/// <summary>This class handles the loading of themes/plugins or other add-ons and their language packs.</summary>
	/// <field name="onAdd" type="tinymce.util.Dispatcher">Fires when a item is added.</field>
}

tinymce.AddOnManager.prototype.get = function(n) {
	/// <summary>Returns the specified add on by the short name.</summary>
	/// <param name="n" type="String">Add-on to look for.</param>
	/// <returns type="">Theme or plugin add-on instance or undefined.</returns>
}

tinymce.AddOnManager.prototype.requireLangPack = function(n) {
	/// <summary>Loads a language pack for the specified add-on.</summary>
	/// <param name="n" type="String">Short name of the add-on.</param>
}

tinymce.AddOnManager.prototype.add = function(id, o) {
	/// <summary>Adds a instance of the add-on by it's short name.</summary>
	/// <param name="id" type="String">Short name/id for the add-on.</param>
	/// <param name="o" type="">Theme or plugin to add.</param>
	/// <returns type="">The same theme or plugin instance that got passed in.</returns>
}

tinymce.AddOnManager.prototype.load = function(n, u, cb, s) {
	/// <summary>Loads an add-on from a specific url.</summary>
	/// <param name="n" type="String">Short name of the add-on that gets loaded.</param>
	/// <param name="u" type="String">URL to the add-on that will get loaded.</param>
	/// <param name="cb" type="function">Optional callback to execute ones the add-on is loaded.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinymce.Theme = function() {
	/// <summary>TinyMCE theme class.</summary>
}

tinymce.Theme.prototype.init = function(editor, url) {
	/// <summary>Initializes the theme.</summary>
	/// <param name="editor" type="tinymce.Editor">Editor instance that created the theme instance.</param>
	/// <param name="url" type="String">Absolute URL where the theme is located.</param>
}

tinymce.Theme.prototype.getInfo = function() {
	/// <summary>Meta info method, this method gets executed when TinyMCE wants to present information about the theme for example in the...</summary>
	/// <returns type="Object">Returns an object with meta information about the theme the current items are longname, author, authorurl, infourl and version.</returns>
}

tinymce.Theme.prototype.renderUI = function(obj) {
	/// <summary>This method is responsible for rendering/generating the overall user interface with toolbars, buttons, iframe containers...</summary>
	/// <param name="obj" type="Object">Object parameter containing the targetNode DOM node that will be replaced visually with an editor instance.</param>
	/// <returns type="Object">an object with items like iframeContainer, editorContainer, sizeContainer, deltaWidth, deltaHeight.</returns>
}

tinymce.Plugin = function() {
	/// <summary>Plugin base class, this is a pseudo class that describes how a plugin is to be created for TinyMCE.</summary>
}

tinymce.Plugin.prototype.init = function(editor, url) {
	/// <summary>Initialization function for the plugin.</summary>
	/// <param name="editor" type="tinymce.Editor">Editor instance that created the plugin instance.</param>
	/// <param name="url" type="String">Absolute URL where the plugin is located.</param>
}

tinymce.Plugin.prototype.getInfo = function() {
	/// <summary>Meta info method, this method gets executed when TinyMCE wants to present information about the plugin for example in th...</summary>
	/// <returns type="Object">Returns an object with meta information about the plugin the current items are longname, author, authorurl, infourl and version.</returns>
}

tinymce.Plugin.prototype.createControl = function(name, controlman) {
	/// <summary>Gets called when a new control instance is created.</summary>
	/// <param name="name" type="String">Control name to create for example "mylistbox"</param>
	/// <param name="controlman" type="tinymce.ControlManager">Control manager/factory to use to create the control.</param>
	/// <returns type="tinymce.ui.Control">Returns a new control instance or null.</returns>
}

tinymce.ControlManager = function(ed, s) {
	/// <summary>This class is responsible for managing UI control instances.</summary>
	/// <param name="ed" type="tinymce.Editor">TinyMCE editor instance to add the control to.</param>
	/// <param name="s" type="Object">Optional settings object for the control manager.</param>
}

tinymce.ControlManager.prototype.get = function(id) {
	/// <summary>Returns a control by id or undefined it it wasn't found.</summary>
	/// <param name="id" type="String">Control instance name.</param>
	/// <returns type="tinymce.ui.Control">Control instance or undefined.</returns>
}

tinymce.ControlManager.prototype.setActive = function(id, s) {
	/// <summary>Sets the active state of a control by id.</summary>
	/// <param name="id" type="String">Control id to set state on.</param>
	/// <param name="s" type="Boolean">Active state true/false.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got activated or null if it wasn't found.</returns>
}

tinymce.ControlManager.prototype.setDisabled = function(id, s) {
	/// <summary>Sets the dsiabled state of a control by id.</summary>
	/// <param name="id" type="String">Control id to set state on.</param>
	/// <param name="s" type="Boolean">Active state true/false.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got disabled or null if it wasn't found.</returns>
}

tinymce.ControlManager.prototype.add = function(Control) {
	/// <summary>Adds a control to the control collection inside the manager.</summary>
	/// <param name="Control" type="tinymce.ui.Control">instance to add to collection.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got passed in.</returns>
}

tinymce.ControlManager.prototype.createControl = function(n) {
	/// <summary>Creates a control by name, when a control is created it will automatically add it to the control collection.</summary>
	/// <param name="n" type="String">Control name to create for example "separator".</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createDropMenu = function(id, s, cc) {
	/// <summary>Creates a drop menu control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new dropdown instance. For example "some menu".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createListBox = function(id, s, cc) {
	/// <summary>Creates a list box control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new listbox instance. For example "styles".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createButton = function(id, s, cc) {
	/// <summary>Creates a button control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new button instance. For example "bold".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createMenuButton = function(id, s, cc) {
	/// <summary>Creates a menu button control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new menu button instance. For example "menu1".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createSplitButton = function(id, s, cc) {
	/// <summary>Creates a split button control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new split button instance. For example "spellchecker".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createColorSplitButton = function(id, s, cc) {
	/// <summary>Creates a color split button control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new color split button instance. For example "forecolor".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createToolbar = function(id, s, cc) {
	/// <summary>Creates a toolbar container control instance by id.</summary>
	/// <param name="id" type="String">Unique id for the new toolbar container control instance. For example "toolbar1".</param>
	/// <param name="s" type="Object">Optional settings object for the control.</param>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.createSeparator = function(cc) {
	/// <summary>Creates a separator control instance.</summary>
	/// <param name="cc" type="Object">Optional control class to use instead of the default one.</param>
	/// <returns type="tinymce.ui.Control">Control instance that got created and added.</returns>
}

tinymce.ControlManager.prototype.setControlType = function(n, c) {
	/// <summary>Overrides a specific control type with a custom class.</summary>
	/// <param name="n" type="string">Name of the control to override for example button or dropmenu.</param>
	/// <param name="c" type="function">Class reference to use instead of the default one.</param>
	/// <returns type="function">Same as the class reference.</returns>
}

tinymce.ControlManager.prototype.destroy = function() {
	/// <summary>Destroy.</summary>
}

tinymce.Editor = function(id, s) {
	/// <summary>This class contains the core logic for a TinyMCE editor.</summary>
	/// <param name="id" type="String">Unique id for the editor.</param>
	/// <param name="s" type="Object">Optional settings string for the editor.</param>
	/// <field name="id" type="String">Editor instance id, normally the same as the div/textarea that was replaced.</field>
	/// <field name="isNotDirty" type="Boolean">State to force the editor to return false on a isDirty call. function ajaxSave() {     var ed = tinyMCE.get('elm1');      // Save contents using some XHR call     alert(ed.getContent());      ed.isNotDirty = 1; // Force not dirty state }</field>
	/// <field name="plugins" type="Object">Name/Value object containting plugin instances. // Execute a method inside a plugin directly tinyMCE.activeEditor.plugins.someplugin.someMethod();</field>
	/// <field name="settings" type="Object">Name/value collection with editor settings. // Get the value of the theme setting tinyMCE.activeEditor.windowManager.alert("You are using the " + tinyMCE.activeEditor.settings.theme + " theme");</field>
	/// <field name="documentBaseURI" type="tinymce.util.URI">URI object to document configured for the TinyMCE instance. // Get relative URL from the location of document_base_url tinyMCE.activeEditor.documentBaseURI.toRelative('/somedir/somefile.htm');  // Get absolute URL from the location of document_base_url tinyMCE.activeEditor.documentBaseURI.toAbsolute('somefile.htm');</field>
	/// <field name="baseURI" type="tinymce.util.URI">URI object to current document that holds the TinyMCE editor instance. // Get relative URL from the location of the API tinyMCE.activeEditor.baseURI.toRelative('/somedir/somefile.htm');  // Get absolute URL from the location of the API tinyMCE.activeEditor.baseURI.toAbsolute('somefile.htm');</field>
	/// <field name="contentCSS" type="Array">Array with CSS files to load into the iframe.</field>
	/// <field name="windowManager" type="tinymce.WindowManager">Window manager reference, use this to open new windows and dialogs. // Shows an alert message tinyMCE.activeEditor.windowManager.alert('Hello world!');  // Opens a new dialog with the file.htm file and the size 320x240 // It also adds a custom parameter this can be retrieved by using tinyMCEPopup.getWindowArg inside the dialog. tinyMCE.activeEditor.windowManager.open({    url : 'file.htm',    width : 320,    height : 240 }, {    custom_param : 1 });</field>
	/// <field name="theme" type="tinymce.Theme">Reference to the theme instance that was used to generate the UI. // Executes a method on the theme directly tinyMCE.activeEditor.theme.someMethod();</field>
	/// <field name="controlManager" type="tinymce.ControlManager">Control manager instance for the editor. Will enables you to create new UI elements and change their states etc. // Disables the bold button tinyMCE.activeEditor.controlManager.setDisabled('bold', true);</field>
	/// <field name="schema" type="tinymce.html.Schema">Schema instance, enables you to validate elements and it's children.</field>
	/// <field name="dom" type="tinymce.dom.DOMUtils">DOM instance for the editor. // Adds a class to all paragraphs within the editor tinyMCE.activeEditor.dom.addClass(tinyMCE.activeEditor.dom.select('p'), 'someclass');</field>
	/// <field name="parser" type="tinymce.html.DomParser">HTML parser will be used when contents is inserted into the editor.</field>
	/// <field name="serializer" type="tinymce.dom.Serializer">DOM serializer for the editor. Will be used when contents is extracted from the editor. // Serializes the first paragraph in the editor into a string tinyMCE.activeEditor.serializer.serialize(tinyMCE.activeEditor.dom.select('p')[0]);</field>
	/// <field name="selection" type="tinymce.dom.Selection">Selection instance for the editor. // Sets some contents to the current selection in the editor tinyMCE.activeEditor.selection.setContent('Some contents');  // Gets the current selection alert(tinyMCE.activeEditor.selection.getContent());  // Selects the first paragraph found tinyMCE.activeEditor.selection.select(tinyMCE.activeEditor.dom.select('p')[0]);</field>
	/// <field name="formatter" type="tinymce.Formatter">Formatter instance.</field>
	/// <field name="undoManager" type="tinymce.UndoManager">Undo manager instance, responsible for handling undo levels. // Undoes the last modification to the editor tinyMCE.activeEditor.undoManager.undo();</field>
	/// <field name="initialized" type="Boolean">Is set to true after the editor instance has been initialized function isEditorInitialized(editor) {     return editor && editor.initialized; }</field>
	/// <field name="onPreInit" type="tinymce.util.Dispatcher">Fires before the initialization of the editor. Editor instance.// Adds an observer to the onPreInit event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onPreInit.add(function(ed) {           console.debug('PreInit: ' + ed.id);       });    } });</field>
	/// <field name="onBeforeRenderUI" type="tinymce.util.Dispatcher">Fires before the initialization of the editor. Editor instance.// Adds an observer to the onBeforeRenderUI event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {      ed.onBeforeRenderUI.add(function(ed, cm) {          console.debug('Before render: ' + ed.id);      });    } });</field>
	/// <field name="onPostRender" type="tinymce.util.Dispatcher">Fires after the rendering has completed. Editor instance.// Adds an observer to the onPostRender event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onPostRender.add(function(ed, cm) {           console.debug('After render: ' + ed.id);       });    } });</field>
	/// <field name="onLoad" type="tinymce.util.Dispatcher">Fires when the onload event on the body occurs. Editor instance.// Adds an observer to the onLoad event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onLoad.add(function(ed, cm) {           console.debug('Document loaded: ' + ed.id);       });    } });</field>
	/// <field name="onInit" type="tinymce.util.Dispatcher">Fires after the initialization of the editor is done. Editor instance.// Adds an observer to the onInit event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onInit.add(function(ed) {           console.debug('Editor is done: ' + ed.id);       });    } });</field>
	/// <field name="onRemove" type="tinymce.util.Dispatcher">Fires when the editor instance is removed from page. Editor instance.// Adds an observer to the onRemove event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onRemove.add(function(ed) {           console.debug('Editor was removed: ' + ed.id);       });    } });</field>
	/// <field name="onActivate" type="tinymce.util.Dispatcher">Fires when the editor is activated. Editor instance.// Adds an observer to the onActivate event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onActivate.add(function(ed) {           console.debug('Editor was activated: ' + ed.id);       });    } });</field>
	/// <field name="onDeactivate" type="tinymce.util.Dispatcher">Fires when the editor is deactivated. Editor instance.// Adds an observer to the onDeactivate event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onDeactivate.add(function(ed) {           console.debug('Editor was deactivated: ' + ed.id);       });    } });</field>
	/// <field name="onClick" type="tinymce.util.Dispatcher">Fires when something in the body of the editor is clicked. Editor instance.W3C DOM Event instance.// Adds an observer to the onClick event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onClick.add(function(ed, e) {           console.debug('Editor was clicked: ' + e.target.nodeName);       });    } });</field>
	/// <field name="onEvent" type="tinymce.util.Dispatcher">Fires when a registered event is intercepted. Editor instance.W3C DOM Event instance.// Adds an observer to the onEvent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onEvent.add(function(ed, e) {          console.debug('Editor event occured: ' + e.target.nodeName);       });    } });</field>
	/// <field name="onMouseUp" type="tinymce.util.Dispatcher">Fires when a mouseup event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onMouseUp event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onMouseUp.add(function(ed, e) {           console.debug('Mouse up event: ' + e.target.nodeName);       });    } });</field>
	/// <field name="onMouseDown" type="tinymce.util.Dispatcher">Fires when a mousedown event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onMouseDown event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onMouseDown.add(function(ed, e) {           console.debug('Mouse down event: ' + e.target.nodeName);       });    } });</field>
	/// <field name="onDblClick" type="tinymce.util.Dispatcher">Fires when a dblclick event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onDblClick event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onDblClick.add(function(ed, e) {          console.debug('Double click event: ' + e.target.nodeName);       });    } });</field>
	/// <field name="onKeyDown" type="tinymce.util.Dispatcher">Fires when a keydown event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onKeyDown event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onKeyDown.add(function(ed, e) {           console.debug('Key down event: ' + e.keyCode);       });    } });</field>
	/// <field name="onKeyUp" type="tinymce.util.Dispatcher">Fires when a keydown event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onKeyUp event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onKeyUp.add(function(ed, e) {           console.debug('Key up event: ' + e.keyCode);       });    } });</field>
	/// <field name="onKeyPress" type="tinymce.util.Dispatcher">Fires when a keypress event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onKeyPress event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onKeyPress.add(function(ed, e) {           console.debug('Key press event: ' + e.keyCode);       });    } });</field>
	/// <field name="onContextMenu" type="tinymce.util.Dispatcher">Fires when a contextmenu event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onContextMenu event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onContextMenu.add(function(ed, e) {            console.debug('Context menu event:' + e.target);       });    } });</field>
	/// <field name="onSubmit" type="tinymce.util.Dispatcher">Fires when a form submit event is intercepted. Editor instance.W3C DOM Event instance.// Adds an observer to the onSubmit event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onSubmit.add(function(ed, e) {            console.debug('Form submit:' + e.target);       });    } });</field>
	/// <field name="onReset" type="tinymce.util.Dispatcher">Fires when a form reset event is intercepted. Editor instance.W3C DOM Event instance.// Adds an observer to the onReset event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onReset.add(function(ed, e) {            console.debug('Form reset:' + e.target);       });    } });</field>
	/// <field name="onPaste" type="tinymce.util.Dispatcher">Fires when a paste event is intercepted inside the editor. Editor instance.W3C DOM Event instance.// Adds an observer to the onPaste event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onPaste.add(function(ed, e) {            console.debug('Pasted plain text');       });    } });</field>
	/// <field name="onPreProcess" type="tinymce.util.Dispatcher">Fires when the Serializer does a preProcess on the contents. Editor instance.PreProcess object.DOM node for the item being serialized.The specified output format normally "html".Is true if the process is on a getContent operation.Is true if the process is on a setContent operation.Is true if the process is on a cleanup operation.// Adds an observer to the onPreProcess event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onPreProcess.add(function(ed, o) {            // Add a class to each paragraph in the editor            ed.dom.addClass(ed.dom.select('p', o.node), 'myclass');       });    } });</field>
	/// <field name="onPostProcess" type="tinymce.util.Dispatcher">Fires when the Serializer does a postProcess on the contents. Editor instance.PreProcess object.// Adds an observer to the onPostProcess event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onPostProcess.add(function(ed, o) {            // Remove all paragraphs and replace with BR            o.content = o.content.replace(/<p[^>]+>|<p>/g, '');            o.content = o.content.replace(/<\/p>/g, '<br />');       });    } });</field>
	/// <field name="onBeforeSetContent" type="tinymce.util.Dispatcher">Fires before new contents is added to the editor. Using for example setContent. Editor instance.// Adds an observer to the onBeforeSetContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onBeforeSetContent.add(function(ed, o) {            // Replaces all a characters with b characters            o.content = o.content.replace(/a/g, 'b');       });    } });</field>
	/// <field name="onBeforeGetContent" type="tinymce.util.Dispatcher">Fires before contents is extracted from the editor using for example getContent. Editor instance.W3C DOM Event instance.// Adds an observer to the onBeforeGetContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onBeforeGetContent.add(function(ed, o) {            console.debug('Before get content.');       });    } });</field>
	/// <field name="onSetContent" type="tinymce.util.Dispatcher">Fires after the contents has been added to the editor using for example onSetContent. Editor instance.// Adds an observer to the onSetContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onSetContent.add(function(ed, o) {            // Replaces all a characters with b characters            o.content = o.content.replace(/a/g, 'b');       });    } });</field>
	/// <field name="onGetContent" type="tinymce.util.Dispatcher">Fires after the contents has been extracted from the editor using for example getContent. Editor instance.// Adds an observer to the onGetContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onGetContent.add(function(ed, o) {           // Replace all a characters with b           o.content = o.content.replace(/a/g, 'b');       });    } });</field>
	/// <field name="onLoadContent" type="tinymce.util.Dispatcher">Fires when the editor gets loaded with contents for example when the load method is executed. Editor instance.// Adds an observer to the onLoadContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onLoadContent.add(function(ed, o) {           // Output the element name           console.debug(o.element.nodeName);       });    } });</field>
	/// <field name="onSaveContent" type="tinymce.util.Dispatcher">Fires when the editor contents gets saved for example when the save method is executed. Editor instance.// Adds an observer to the onSaveContent event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onSaveContent.add(function(ed, o) {           // Output the element name           console.debug(o.element.nodeName);       });    } });</field>
	/// <field name="onNodeChange" type="tinymce.util.Dispatcher">Fires when the user changes node location using the mouse or keyboard. Editor instance.// Adds an observer to the onNodeChange event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onNodeChange.add(function(ed, cm, e) {           // Activates the link button when the caret is placed in a anchor element           if (e.nodeName == 'A')              cm.setActive('link', true);       });    } });</field>
	/// <field name="onChange" type="tinymce.util.Dispatcher">Fires when a new undo level is added to the editor. Editor instance.// Adds an observer to the onChange event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) { 	  ed.onChange.add(function(ed, l) { 		  console.debug('Editor contents was modified. Contents: ' + l.content); 	  });    } });</field>
	/// <field name="onBeforeExecCommand" type="tinymce.util.Dispatcher">Fires before a command gets executed for example "Bold". Editor instance.// Adds an observer to the onBeforeExecCommand event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onBeforeExecCommand.add(function(ed, cmd, ui, val) {           console.debug('Command is to be executed: ' + cmd);       });    } });</field>
	/// <field name="onExecCommand" type="tinymce.util.Dispatcher">Fires after a command is executed for example "Bold". Editor instance.// Adds an observer to the onExecCommand event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onExecCommand.add(function(ed, cmd, ui, val) {           console.debug('Command was executed: ' + cmd);       });    } });</field>
	/// <field name="onUndo" type="tinymce.util.Dispatcher">Fires when the contents is undo:ed. Editor instance.{Object} level Undo level object. @ example // Adds an observer to the onUndo event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onUndo.add(function(ed, level) {           console.debug('Undo was performed: ' + level.content);       });    } });</field>
	/// <field name="onRedo" type="tinymce.util.Dispatcher">Fires when the contents is redo:ed. Editor instance.Undo level object.// Adds an observer to the onRedo event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onRedo.add(function(ed, level) {           console.debug('Redo was performed: ' +level.content);       });    } });</field>
	/// <field name="onVisualAid" type="tinymce.util.Dispatcher">Fires when visual aids is enabled/disabled. Editor instance.// Adds an observer to the onVisualAid event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onVisualAid.add(function(ed, e, s) {           console.debug('onVisualAid event: ' + ed.id + ", State: " + s);       });    } });</field>
	/// <field name="onSetProgressState" type="tinymce.util.Dispatcher">Fires when the progress throbber is shown above the editor. Editor instance.// Adds an observer to the onSetProgressState event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onSetProgressState.add(function(ed, b) {            if (b)                 console.debug('SHOW!');            else                 console.debug('HIDE!');       });    } });</field>
	/// <field name="onSetAttrib" type="tinymce.util.Dispatcher">Fires after an attribute is set using setAttrib. Editor instance.// Adds an observer to the onSetAttrib event using tinyMCE.init tinyMCE.init({    ...    setup : function(ed) {       ed.onSetAttrib.add(function(ed, node, attribute, attributeValue) {            console.log('onSetAttrib tag');       });    } });</field>
}

tinymce.Editor.prototype.render = function() {
	/// <summary>Renderes the editor/adds it to the page.</summary>
}

tinymce.Editor.prototype.init = function() {
	/// <summary>Initializes the editor this will be called automatically when all plugins/themes and language packs are loaded by the re...</summary>
}

tinymce.Editor.prototype.setupIframe = function() {
	/// <summary>This method get called by the init method ones the iframe is loaded.</summary>
}

tinymce.Editor.prototype.setupContentEditable = function() {
	/// <summary>Sets up the contentEditable mode.</summary>
}

tinymce.Editor.prototype.focus = function(sf) {
	/// <summary>Focuses/activates the editor.</summary>
	/// <param name="sf" type="Boolean">Skip DOM focus. Just set is as the active editor.</param>
}

tinymce.Editor.prototype.execCallback = function(n) {
	/// <summary>Executes a legacy callback.</summary>
	/// <param name="n" type="String">Name of the callback to execute.</param>
	/// <returns type="Object">Return value passed from callback function.</returns>
}

tinymce.Editor.prototype.translate = function(s) {
	/// <summary>Translates the specified string by replacing variables with language pack items it will also check if there is a key mat...</summary>
	/// <param name="s" type="String">String to translate by the language pack data.</param>
	/// <returns type="String">Translated string.</returns>
}

tinymce.Editor.prototype.getLang = function(n, dv) {
	/// <summary>Returns a language pack item by name/key.</summary>
	/// <param name="n" type="String">Name/key to get from the language pack.</param>
	/// <param name="dv" type="String">Optional default value to retrive.</param>
}

tinymce.Editor.prototype.getParam = function(n, dv, ty) {
	/// <summary>Returns a configuration parameter by name.</summary>
	/// <param name="n" type="String">Configruation parameter to retrive.</param>
	/// <param name="dv" type="String">Optional default value to return.</param>
	/// <param name="ty" type="String">Optional type parameter.</param>
	/// <returns type="String">Configuration parameter value or default value.</returns>
}

tinymce.Editor.prototype.nodeChanged = function(o) {
	/// <summary>Distpaches out a onNodeChange event to all observers.</summary>
	/// <param name="o" type="Object">Optional object to pass along for the node changed event.</param>
}

tinymce.Editor.prototype.addButton = function(n, s) {
	/// <summary>Adds a button that later gets created by the ControlManager.</summary>
	/// <param name="n" type="String">Button name to add.</param>
	/// <param name="s" type="Object">Settings object with title, cmd etc.</param>
}

tinymce.Editor.prototype.addCommand = function(name, callback, scope) {
	/// <summary>Adds a custom command to the editor, you can also override existing commands with this method.</summary>
	/// <param name="name" type="String">Command name to add/override.</param>
	/// <param name="callback" type="tinymce.Editor.addCommandCallback">Function to execute when the command occurs.</param>
	/// <param name="scope" type="Object">Optional scope to execute the function in.</param>
}

tinymce.Editor.prototype.addQueryStateHandler = function(name, callback, scope) {
	/// <summary>Adds a custom query state command to the editor, you can also override existing commands with this method.</summary>
	/// <param name="name" type="String">Command name to add/override.</param>
	/// <param name="callback" type="tinymce.Editor.addQueryStateHandlerCallback">Function to execute when the command state retrival occurs.</param>
	/// <param name="scope" type="Object">Optional scope to execute the function in.</param>
}

tinymce.Editor.prototype.addQueryValueHandler = function(name, callback, scope) {
	/// <summary>Adds a custom query value command to the editor, you can also override existing commands with this method.</summary>
	/// <param name="name" type="String">Command name to add/override.</param>
	/// <param name="callback" type="tinymce.Editor.addQueryValueHandlerCallback">Function to execute when the command value retrival occurs.</param>
	/// <param name="scope" type="Object">Optional scope to execute the function in.</param>
}

tinymce.Editor.prototype.addShortcut = function(pa, desc, cmd_func, sc) {
	/// <summary>Adds a keyboard shortcut for some command or function.</summary>
	/// <param name="pa" type="String">Shortcut pattern. Like for example: ctrl+alt+o.</param>
	/// <param name="desc" type="String">Text description for the command.</param>
	/// <param name="cmd_func" type="">Command name string or function to execute when the key is pressed.</param>
	/// <param name="sc" type="Object">Optional scope to execute the function in.</param>
	/// <returns type="Boolean">true/false state if the shortcut was added or not.</returns>
}

tinymce.Editor.prototype.execCommand = function(cmd, ui, val, a) {
	/// <summary>Executes a command on the current instance.</summary>
	/// <param name="cmd" type="String">Command name to execute, for example mceLink or Bold.</param>
	/// <param name="ui" type="Boolean">True/false state if a UI (dialog) should be presented or not.</param>
	/// <param name="val" type="mixed">Optional command value, this can be anything.</param>
	/// <param name="a" type="Object">Optional arguments object.</param>
	/// <returns type="Boolean">True/false if the command was executed or not.</returns>
}

tinymce.Editor.prototype.queryCommandState = function(cmd) {
	/// <summary>Returns a command specific state, for example if bold is enabled or not.</summary>
	/// <param name="cmd" type="string">Command to query state from.</param>
	/// <returns type="Boolean">Command specific state, for example if bold is enabled or not.</returns>
}

tinymce.Editor.prototype.queryCommandValue = function(c) {
	/// <summary>Returns a command specific value, for example the current font size.</summary>
	/// <param name="c" type="string">Command to query value from.</param>
	/// <returns type="Object">Command specific value, for example the current font size.</returns>
}

tinymce.Editor.prototype.show = function() {
	/// <summary>Shows the editor and hides any textarea/div that the editor is supposed to replace.</summary>
}

tinymce.Editor.prototype.hide = function() {
	/// <summary>Hides the editor and shows any textarea/div that the editor is supposed to replace.</summary>
}

tinymce.Editor.prototype.isHidden = function() {
	/// <summary>Returns true/false if the editor is hidden or not.</summary>
	/// <returns type="Boolean">True/false if the editor is hidden or not.</returns>
}

tinymce.Editor.prototype.setProgressState = function(b, ti, o) {
	/// <summary>Sets the progress state, this will display a throbber/progess for the editor.</summary>
	/// <param name="b" type="Boolean">Boolean state if the progress should be shown or hidden.</param>
	/// <param name="ti" type="Number" integer="true">Optional time to wait before the progress gets shown.</param>
	/// <param name="o" type="Object">Optional object to pass to the progress observers.</param>
	/// <returns type="Boolean">Same as the input state.</returns>
}

tinymce.Editor.prototype.load = function(o) {
	/// <summary>Loads contents from the textarea or div element that got converted into an editor instance.</summary>
	/// <param name="o" type="Object">Optional content object, this gets passed around through the whole load process.</param>
	/// <returns type="String">HTML string that got set into the editor.</returns>
}

tinymce.Editor.prototype.save = function(o) {
	/// <summary>Saves the contents from a editor out to the textarea or div element that got converted into an editor instance.</summary>
	/// <param name="o" type="Object">Optional content object, this gets passed around through the whole save process.</param>
	/// <returns type="String">HTML string that got set into the textarea/div.</returns>
}

tinymce.Editor.prototype.setContent = function(content, args) {
	/// <summary>Sets the specified content to the editor instance, this will cleanup the content before it gets set using the different ...</summary>
	/// <param name="content" type="String">Content to set to editor, normally HTML contents but can be other formats as well.</param>
	/// <param name="args" type="Object">Optional content object, this gets passed around through the whole set process.</param>
	/// <returns type="String">HTML string that got set into the editor.</returns>
}

tinymce.Editor.prototype.getContent = function(args) {
	/// <summary>Gets the content from the editor instance, this will cleanup the content before it gets returned using the different cle...</summary>
	/// <param name="args" type="Object">Optional content object, this gets passed around through the whole get process.</param>
	/// <returns type="String">Cleaned content string, normally HTML contents.</returns>
}

tinymce.Editor.prototype.isDirty = function() {
	/// <summary>Returns true/false if the editor is dirty or not.</summary>
	/// <returns type="Boolean">True/false if the editor is dirty or not. It will get dirty if the user has made modifications to the contents.</returns>
}

tinymce.Editor.prototype.getContainer = function() {
	/// <summary>Returns the editors container element.</summary>
	/// <returns type="Element" domElement="true">HTML DOM element for the editor container.</returns>
}

tinymce.Editor.prototype.getContentAreaContainer = function() {
	/// <summary>Returns the editors content area container element.</summary>
	/// <returns type="Element" domElement="true">HTML DOM element for the editor area container.</returns>
}

tinymce.Editor.prototype.getElement = function() {
	/// <summary>Returns the target element/textarea that got replaced with a TinyMCE editor instance.</summary>
	/// <returns type="Element" domElement="true">HTML DOM element for the replaced element.</returns>
}

tinymce.Editor.prototype.getWin = function() {
	/// <summary>Returns the iframes window object.</summary>
	/// <returns type="Window">Iframe DOM window object.</returns>
}

tinymce.Editor.prototype.getDoc = function() {
	/// <summary>Returns the iframes document object.</summary>
	/// <returns type="Document">Iframe DOM document object.</returns>
}

tinymce.Editor.prototype.getBody = function() {
	/// <summary>Returns the iframes body element.</summary>
	/// <returns type="Element" domElement="true">Iframe body element.</returns>
}

tinymce.Editor.prototype.convertURL = function(u, n, Tag) {
	/// <summary>URL converter function this gets executed each time a user adds an img, a or any other element that has a URL in it.</summary>
	/// <param name="u" type="string">URL to convert.</param>
	/// <param name="n" type="string">Attribute name src, href etc.</param>
	/// <param name="Tag" type="">name or HTML DOM element depending on HTML or DOM insert.</param>
	/// <returns type="string">Converted URL string.</returns>
}

tinymce.Editor.prototype.addVisual = function(e) {
	/// <summary>Adds visual aid for tables, anchors etc so they can be more easily edited inside the editor.</summary>
	/// <param name="e" type="Element" domElement="true">Optional root element to loop though to find tables etc that needs the visual aid.</param>
}

tinymce.Editor.prototype.remove = function() {
	/// <summary>Removes the editor from the dom and tinymce collection.</summary>
}

tinymce.Editor.prototype.destroy = function(s) {
	/// <summary>Destroys the editor instance by removing all events, element references or other resources that could leak memory.</summary>
	/// <param name="s" type="Boolean">Optional state if the destroy is an automatic destroy or user called one.</param>
}

tinymce.EditorCommands = function() {
	/// <summary>This class enables you to add custom editor commands and it contains overrides for native browser commands to address va...</summary>
}

tinymce.EditorCommands.prototype.execCommand = function(command, ui, value) {
	/// <summary>Executes the specified command.</summary>
	/// <param name="command" type="String">Command to execute.</param>
	/// <param name="ui" type="Boolean">Optional user interface state.</param>
	/// <param name="value" type="Object">Optional value for command.</param>
	/// <returns type="Boolean">true/false if the command was found or not.</returns>
}

tinymce.EditorCommands.prototype.queryCommandState = function(command) {
	/// <summary>Queries the current state for a command for example if the current selection is "bold".</summary>
	/// <param name="command" type="String">Command to check the state of.</param>
	/// <returns type="">true/false if the selected contents is bold or not, -1 if it's not found.</returns>
}

tinymce.EditorCommands.prototype.queryCommandValue = function(command) {
	/// <summary>Queries the command value for example the current fontsize.</summary>
	/// <param name="command" type="String">Command to check the value of.</param>
	/// <returns type="Object">Command value of false if it's not found.</returns>
}

tinymce.EditorCommands.prototype.addCommands = function(command_list, type) {
	/// <summary>Adds commands to the command collection.</summary>
	/// <param name="command_list" type="Object">Name/value collection with commands to add, the names can also be comma separated.</param>
	/// <param name="type" type="String">Optional type to add, defaults to exec. Can be value or state as well.</param>
}

tinymce.Formatter = function() {
	/// <summary>Text formatter engine class.</summary>
}

tinymce.Formatter.prototype.get = function(name) {
	/// <summary>Returns the format by name or all formats if no name is specified.</summary>
	/// <param name="name" type="String">Optional name to retrive by.</param>
	/// <returns type="">Array/Object with all registred formats or a specific format.</returns>
}

tinymce.Formatter.prototype.register = function(name, format) {
	/// <summary>Registers a specific format by name.</summary>
	/// <param name="name" type="">Name of the format for example "bold".</param>
	/// <param name="format" type="">Optional format object or array of format variants can only be omitted if the first arg is an object.</param>
}

tinymce.Formatter.prototype.apply = function(name, vars, node) {
	/// <summary>Applies the specified format to the current selection or specified node.</summary>
	/// <param name="name" type="String">Name of format to apply.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace within format before applying it.</param>
	/// <param name="node" type="Node">Optional node to apply the format to defaults to current selection.</param>
}

tinymce.Formatter.prototype.remove = function(name, vars, node) {
	/// <summary>Removes the specified format from the current selection or specified node.</summary>
	/// <param name="name" type="String">Name of format to remove.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace within format before removing it.</param>
	/// <param name="node" type="">Optional node or DOM range to remove the format from defaults to current selection.</param>
}

tinymce.Formatter.prototype.toggle = function(name, vars, node) {
	/// <summary>Toggles the specified format on/off.</summary>
	/// <param name="name" type="String">Name of format to apply/remove.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace within format before applying/removing it.</param>
	/// <param name="node" type="Node">Optional node to apply the format to or remove from. Defaults to current selection.</param>
}

tinymce.Formatter.prototype.matchNode = function(node, name, vars, similar) {
	/// <summary>Return true/false if the specified node has the specified format.</summary>
	/// <param name="node" type="Node">Node to check the format on.</param>
	/// <param name="name" type="String">Format name to check.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace before checking it.</param>
	/// <param name="similar" type="Boolean">Match format that has similar properties.</param>
	/// <returns type="Object">Returns the format object it matches or undefined if it doesn't match.</returns>
}

tinymce.Formatter.prototype.match = function(name, vars, node) {
	/// <summary>Matches the current selection or specified node against the specified format name.</summary>
	/// <param name="name" type="String">Name of format to match.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace before checking it.</param>
	/// <param name="node" type="Node">Optional node to check.</param>
	/// <returns type="boolean">true/false if the specified selection/node matches the format.</returns>
}

tinymce.Formatter.prototype.matchAll = function(names, vars) {
	/// <summary>Matches the current selection against the array of formats and returns a new array with matching formats.</summary>
	/// <param name="names" type="Array">Name of format to match.</param>
	/// <param name="vars" type="Object">Optional list of variables to replace before checking it.</param>
	/// <returns type="Array">Array with matched formats.</returns>
}

tinymce.Formatter.prototype.canApply = function(name) {
	/// <summary>Returns true/false if the specified format can be applied to the current selection or not.</summary>
	/// <param name="name" type="String">Name of format to check.</param>
	/// <returns type="boolean">true/false if the specified format can be applied to the current selection/node.</returns>
}

tinymce.UndoManager = function() {
	/// <summary>This class handles the undo/redo history levels for the editor.</summary>
	/// <field name="onAdd" type="tinymce.util.Dispatcher">This event will fire each time a new undo level is added to the undo manager. UndoManager instance that got the new level.The new level object containing a bookmark and contents.</field>
	/// <field name="onUndo" type="tinymce.util.Dispatcher">This event will fire when the user make an undo of a change. UndoManager instance that got the new level.The old level object containing a bookmark and contents.</field>
	/// <field name="onRedo" type="tinymce.util.Dispatcher">This event will fire when the user make an redo of a change. UndoManager instance that got the new level.The old level object containing a bookmark and contents.</field>
}

tinymce.UndoManager.prototype.beforeChange = function() {
	/// <summary>Stores away a bookmark to be used when performing an undo action so that the selection is before the change has been mad...</summary>
}

tinymce.UndoManager.prototype.add = function(l) {
	/// <summary>Adds a new undo level/snapshot to the undo list.</summary>
	/// <param name="l" type="Object">Optional undo level object to add.</param>
	/// <returns type="Object">Undo level that got added or null it a level wasn't needed.</returns>
}

tinymce.UndoManager.prototype.undo = function() {
	/// <summary>Undoes the last action.</summary>
	/// <returns type="Object">Undo level or null if no undo was performed.</returns>
}

tinymce.UndoManager.prototype.redo = function() {
	/// <summary>Redoes the last action.</summary>
	/// <returns type="Object">Redo level or null if no redo was performed.</returns>
}

tinymce.UndoManager.prototype.clear = function() {
	/// <summary>Removes all undo levels.</summary>
}

tinymce.UndoManager.prototype.hasUndo = function() {
	/// <summary>Returns true/false if the undo manager has any undo levels.</summary>
	/// <returns type="Boolean">true/false if the undo manager has any undo levels.</returns>
}

tinymce.UndoManager.prototype.hasRedo = function() {
	/// <summary>Returns true/false if the undo manager has any redo levels.</summary>
	/// <returns type="Boolean">true/false if the undo manager has any redo levels.</returns>
}

tinymce.WindowManager = function(ed) {
	/// <summary>This class handles the creation of native windows and dialogs.</summary>
	/// <param name="ed" type="tinymce.Editor">Editor instance that the windows are bound to.</param>
}

tinymce.WindowManager.prototype.open = function(s, p) {
	/// <summary>Opens a new window.</summary>
	/// <param name="s" type="Object">Optional name/value settings collection contains things like width/height/url etc.Window title.URL of the file to open in the window.Width in pixels.Height in pixels.Specifies whether the popup window is resizable or not.Specifies whether the popup window has a "maximize" button and can get maximized or not.Specifies whether to display in-line (set to 1 or true for in-line display; requires inlinepopups plugin).Optional CSS to use in the popup. Set to false to remove the default one.Specifies whether translation should occur or not of i18 key strings. Default is true.Specifies whether a previously opened popup window is to be closed or not (like when calling the file browser window over the advlink popup).Specifies whether the popup window can have scrollbars if required (i.e. content larger than the popup size specified).</param>
	/// <param name="p" type="Object">Optional parameters/arguments collection can be used by the dialogs to retrive custom parameters.url to plugin if opening plugin window that calls tinyMCEPopup.requireLangPack() and needs access to the plugin language js files</param>
}

tinymce.WindowManager.prototype.close = function(w) {
	/// <summary>Closes the specified window.</summary>
	/// <param name="w" type="Window">Native window object to close.</param>
}

tinymce.WindowManager.prototype.createInstance = function(cl) {
	/// <summary>Creates a instance of a class.</summary>
	/// <param name="cl" type="String">Class name to create an instance of.</param>
	/// <returns type="Object">Instance of the specified class.</returns>
}

tinymce.WindowManager.prototype.confirm = function(t, cb, s) {
	/// <summary>Creates a confirm dialog.</summary>
	/// <param name="t" type="String">Title for the new confirm dialog.</param>
	/// <param name="cb" type="function">Callback function to be executed after the user has selected ok or cancel.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinymce.WindowManager.prototype.alert = function(t, cb, s) {
	/// <summary>Creates a alert dialog.</summary>
	/// <param name="t" type="String">Title for the new alert dialog.</param>
	/// <param name="cb" type="function">Callback function to be executed after the user has selected ok.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinymce.dom.DOMUtils = function(d, s) {
	/// <summary>Utility class for various DOM manipulation and retrival functions.</summary>
	/// <param name="d" type="Document">Document reference to bind the utility class to.</param>
	/// <param name="s" type="settings">Optional settings collection.</param>
}

tinymce.dom.DOMUtils.prototype.isBlock = function(node) {
	/// <summary>Returns true/false if the specified element is a block element or not.</summary>
	/// <param name="node" type="">Element/Node to check.</param>
	/// <returns type="Boolean">True/False state if the node is a block element or not.</returns>
}

tinymce.dom.DOMUtils.prototype.getRoot = function() {
	/// <summary>Returns the root node of the document this is normally the body but might be a DIV.</summary>
	/// <returns type="Element" domElement="true">Root element for the utility class.</returns>
}

tinymce.dom.DOMUtils.prototype.getViewPort = function(w) {
	/// <summary>Returns the viewport of the window.</summary>
	/// <param name="w" type="Window">Optional window to get viewport of.</param>
	/// <returns type="Object">Viewport object with fields x, y, w and h.</returns>
}

tinymce.dom.DOMUtils.prototype.getRect = function(e) {
	/// <summary>Returns the rectangle for a specific element.</summary>
	/// <param name="e" type="">Element object or element ID to get rectange from.</param>
	/// <returns type="object">Rectange for specified element object with x, y, w, h fields.</returns>
}

tinymce.dom.DOMUtils.prototype.getSize = function(e) {
	/// <summary>Returns the size dimensions of the specified element.</summary>
	/// <param name="e" type="">Element object or element ID to get rectange from.</param>
	/// <returns type="object">Rectange for specified element object with w, h fields.</returns>
}

tinymce.dom.DOMUtils.prototype.getParent = function(n, f, r) {
	/// <summary>Returns a node by the specified selector function.</summary>
	/// <param name="n" type="">DOM node to search parents on or ID string.</param>
	/// <param name="f" type="function">Selection function to execute on each node or CSS pattern.</param>
	/// <param name="r" type="Node">Optional root element, never go below this point.</param>
	/// <returns type="Node">DOM Node or null if it wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.getParents = function(n, f, r) {
	/// <summary>Returns a node list of all parents matching the specified selector function or pattern.</summary>
	/// <param name="n" type="">DOM node to search parents on or ID string.</param>
	/// <param name="f" type="function">Selection function to execute on each node or CSS pattern.</param>
	/// <param name="r" type="Node">Optional root element, never go below this point.</param>
	/// <returns type="Array">Array of nodes or null if it wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.get = function(n) {
	/// <summary>Returns the specified element by ID or the input element if it isn't a string.</summary>
	/// <param name="n" type="">Element id to look for or element to just pass though.</param>
	/// <returns type="Element" domElement="true">Element matching the specified id or null if it wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.getNext = function(node, selector) {
	/// <summary>Returns the next node that matches selector or function</summary>
	/// <param name="node" type="Node">Node to find siblings from.</param>
	/// <param name="selector" type="">Selector CSS expression or function.</param>
	/// <returns type="Node">Next node item matching the selector or null if it wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.getPrev = function(node, selector) {
	/// <summary>Returns the previous node that matches selector or function</summary>
	/// <param name="node" type="Node">Node to find siblings from.</param>
	/// <param name="selector" type="">Selector CSS expression or function.</param>
	/// <returns type="Node">Previous node item matching the selector or null if it wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.select = function(p, s) {
	/// <summary>Selects specific elements by a CSS level 3 pattern.</summary>
	/// <param name="p" type="String">CSS level 1 pattern to select/find elements by.</param>
	/// <param name="s" type="Object">Optional root element/scope element to search in.</param>
	/// <returns type="Array">Array with all matched elements.</returns>
}

tinymce.dom.DOMUtils.prototype.is = function(n, selector) {
	/// <summary>Returns true/false if the specified element matches the specified css pattern.</summary>
	/// <param name="n" type="">DOM node to match or an array of nodes to match.</param>
	/// <param name="selector" type="String">CSS pattern to match the element agains.</param>
}

tinymce.dom.DOMUtils.prototype.add = function(Element, n, a, h, c) {
	/// <summary>Adds the specified element to another element or elements.</summary>
	/// <param name="Element" type="">id string, DOM node element or array of id's or elements to add to.</param>
	/// <param name="n" type="">Name of new element to add or existing element to add.</param>
	/// <param name="a" type="Object">Optional object collection with arguments to add to the new element(s).</param>
	/// <param name="h" type="String">Optional inner HTML contents to add for each element.</param>
	/// <param name="c" type="Boolean">Optional internal state to indicate if it should create or add.</param>
	/// <returns type="">Element that got created or array with elements if multiple elements where passed.</returns>
}

tinymce.dom.DOMUtils.prototype.create = function(n, a, h) {
	/// <summary>Creates a new element.</summary>
	/// <param name="n" type="String">Name of new element.</param>
	/// <param name="a" type="Object">Optional object name/value collection with element attributes.</param>
	/// <param name="h" type="String">Optional HTML string to set as inner HTML of the element.</param>
	/// <returns type="Element" domElement="true">HTML DOM node element that got created.</returns>
}

tinymce.dom.DOMUtils.prototype.createHTML = function(n, a, h) {
	/// <summary>Create HTML string for element.</summary>
	/// <param name="n" type="String">Name of new element.</param>
	/// <param name="a" type="Object">Optional object name/value collection with element attributes.</param>
	/// <param name="h" type="String">Optional HTML string to set as inner HTML of the element.</param>
	/// <returns type="String">String with new HTML element like for example: <a href="#">test</a>.</returns>
}

tinymce.dom.DOMUtils.prototype.remove = function(node, keep_children) {
	/// <summary>Removes/deletes the specified element(s) from the DOM.</summary>
	/// <param name="node" type="">ID of element or DOM element object or array containing multiple elements/ids.</param>
	/// <param name="keep_children" type="Boolean">Optional state to keep children or not. If set to true all children will be placed at the location of the removed element.</param>
	/// <returns type="">HTML DOM element that got removed or array of elements depending on input.</returns>
}

tinymce.dom.DOMUtils.prototype.setStyle = function(n, na, v) {
	/// <summary>Sets the CSS style value on a HTML element.</summary>
	/// <param name="n" type="">HTML element/Element ID or Array of elements/ids to set CSS style value on.</param>
	/// <param name="na" type="String">Name of the style value to set.</param>
	/// <param name="v" type="String">Value to set on the style.</param>
}

tinymce.dom.DOMUtils.prototype.getStyle = function(n, na, c) {
	/// <summary>Returns the current style or runtime/computed value of a element.</summary>
	/// <param name="n" type="">HTML element or element id string to get style from.</param>
	/// <param name="na" type="String">Style name to return.</param>
	/// <param name="c" type="Boolean">Computed style.</param>
	/// <returns type="String">Current style or computed style value of a element.</returns>
}

tinymce.dom.DOMUtils.prototype.setStyles = function(e, o) {
	/// <summary>Sets multiple styles on the specified element(s).</summary>
	/// <param name="e" type="">DOM element, element id string or array of elements/ids to set styles on.</param>
	/// <param name="o" type="Object">Name/Value collection of style items to add to the element(s).</param>
}

tinymce.dom.DOMUtils.prototype.setAttrib = function(e, n, v) {
	/// <summary>Sets the specified attributes value of a element or elements.</summary>
	/// <param name="e" type="">DOM element, element id string or array of elements/ids to set attribute on.</param>
	/// <param name="n" type="String">Name of attribute to set.</param>
	/// <param name="v" type="String">Value to set on the attribute of this value is falsy like null 0 or '' it will remove the attribute instead.</param>
}

tinymce.dom.DOMUtils.prototype.setAttribs = function(e, o) {
	/// <summary>Sets the specified attributes of a element or elements.</summary>
	/// <param name="e" type="">DOM element, element id string or array of elements/ids to set attributes on.</param>
	/// <param name="o" type="Object">Name/Value collection of attribute items to add to the element(s).</param>
}

tinymce.dom.DOMUtils.prototype.getAttrib = function(e, n, dv) {
	/// <summary>Returns the specified attribute by name.</summary>
	/// <param name="e" type="">Element string id or DOM element to get attribute from.</param>
	/// <param name="n" type="String">Name of attribute to get.</param>
	/// <param name="dv" type="String">Optional default value to return if the attribute didn't exist.</param>
	/// <returns type="String">Attribute value string, default value or null if the attribute wasn't found.</returns>
}

tinymce.dom.DOMUtils.prototype.getPos = function(n, ro) {
	/// <summary>Returns the absolute x, y position of a node.</summary>
	/// <param name="n" type="">HTML element or element id to get x, y position from.</param>
	/// <param name="ro" type="Element" domElement="true">Optional root element to stop calculations at.</param>
	/// <returns type="object">Absolute position of the specified element object with x, y fields.</returns>
}

tinymce.dom.DOMUtils.prototype.parseStyle = function(st) {
	/// <summary>Parses the specified style value into an object collection.</summary>
	/// <param name="st" type="String">Style value to parse for example: border:1px solid red;.</param>
	/// <returns type="Object">Object representation of that style like {border : '1px solid red'}</returns>
}

tinymce.dom.DOMUtils.prototype.serializeStyle = function(o, name) {
	/// <summary>Serializes the specified style object into a string.</summary>
	/// <param name="o" type="Object">Object to serialize as string for example: {border : '1px solid red'}</param>
	/// <param name="name" type="String">Optional element name.</param>
	/// <returns type="String">String representation of the style object for example: border: 1px solid red.</returns>
}

tinymce.dom.DOMUtils.prototype.loadCSS = function(u) {
	/// <summary>Imports/loads the specified CSS file into the document bound to the class.</summary>
	/// <param name="u" type="String">URL to CSS file to load.</param>
}

tinymce.dom.DOMUtils.prototype.addClass = function(Element, c) {
	/// <summary>Adds a class to the specified element or elements.</summary>
	/// <param name="Element" type="">ID string or DOM element or array with elements or IDs.</param>
	/// <param name="c" type="String">Class name to add to each element.</param>
	/// <returns type="">String with new class value or array with new class values for all elements.</returns>
}

tinymce.dom.DOMUtils.prototype.removeClass = function(Element, c) {
	/// <summary>Removes a class from the specified element or elements.</summary>
	/// <param name="Element" type="">ID string or DOM element or array with elements or IDs.</param>
	/// <param name="c" type="String">Class name to remove to each element.</param>
	/// <returns type="">String with new class value or array with new class values for all elements.</returns>
}

tinymce.dom.DOMUtils.prototype.hasClass = function(n, c) {
	/// <summary>Returns true if the specified element has the specified class.</summary>
	/// <param name="n" type="">HTML element or element id string to check CSS class on.</param>
	/// <param name="c" type="String">CSS class to check for.</param>
	/// <returns type="Boolean">true/false if the specified element has the specified class.</returns>
}

tinymce.dom.DOMUtils.prototype.show = function(e) {
	/// <summary>Shows the specified element(s) by ID by setting the "display" style.</summary>
	/// <param name="e" type="">ID of DOM element or DOM element or array with elements or IDs to show.</param>
}

tinymce.dom.DOMUtils.prototype.hide = function(e) {
	/// <summary>Hides the specified element(s) by ID by setting the "display" style.</summary>
	/// <param name="e" type="">ID of DOM element or DOM element or array with elements or IDs to hide.</param>
}

tinymce.dom.DOMUtils.prototype.isHidden = function(e) {
	/// <summary>Returns true/false if the element is hidden or not by checking the "display" style.</summary>
	/// <param name="e" type="">Id or element to check display state on.</param>
	/// <returns type="Boolean">true/false if the element is hidden or not.</returns>
}

tinymce.dom.DOMUtils.prototype.uniqueId = function(p) {
	/// <summary>Returns a unique id.</summary>
	/// <param name="p" type="String">Optional prefix to add infront of all ids defaults to "mce_".</param>
	/// <returns type="String">Unique id.</returns>
}

tinymce.dom.DOMUtils.prototype.setHTML = function(e, h) {
	/// <summary>Sets the specified HTML content inside the element or elements.</summary>
	/// <param name="e" type="">DOM element, element id string or array of elements/ids to set HTML inside.</param>
	/// <param name="h" type="String">HTML content to set as inner HTML of the element.</param>
}

tinymce.dom.DOMUtils.prototype.getOuterHTML = function(elm) {
	/// <summary>Returns the outer HTML of an element.</summary>
	/// <param name="elm" type="">Element ID or element object to get outer HTML from.</param>
	/// <returns type="String">Outer HTML string.</returns>
}

tinymce.dom.DOMUtils.prototype.setOuterHTML = function(e, h, d) {
	/// <summary>Sets the specified outer HTML on a element or elements.</summary>
	/// <param name="e" type="">DOM element, element id string or array of elements/ids to set outer HTML on.</param>
	/// <param name="h" type="Object">HTML code to set as outer value for the element.</param>
	/// <param name="d" type="Document">Optional document scope to use in this process defaults to the document of the DOM class.</param>
}

tinymce.dom.DOMUtils.prototype.decode = function(s) {
	/// <summary>Entity decode a string, resolves any HTML entities like &aring;.</summary>
	/// <param name="s" type="String">String to decode entities on.</param>
	/// <returns type="String">Entity decoded string.</returns>
}

tinymce.dom.DOMUtils.prototype.encode = function(text) {
	/// <summary>Entity encodes a string, encodes the most common entities <>"& into entities.</summary>
	/// <param name="text" type="String">String to encode with entities.</param>
	/// <returns type="String">Entity encoded string.</returns>
}

tinymce.dom.DOMUtils.prototype.insertAfter = function(node, reference_node) {
	/// <summary>Inserts a element after the reference element.</summary>
	/// <param name="node" type="Element" domElement="true">Element to insert after the reference.</param>
	/// <param name="reference_node" type="">Reference element, element id or array of elements to insert after.</param>
	/// <returns type="">Element that got added or an array with elements.</returns>
}

tinymce.dom.DOMUtils.prototype.replace = function(n, o, k) {
	/// <summary>Replaces the specified element or elements with the specified element, the new element will be cloned if multiple inputs...</summary>
	/// <param name="n" type="Element" domElement="true">New element to replace old ones with.</param>
	/// <param name="o" type="">Element DOM node, element id or array of elements or ids to replace.</param>
	/// <param name="k" type="Boolean">Optional keep children state, if set to true child nodes from the old object will be added to new ones.</param>
}

tinymce.dom.DOMUtils.prototype.rename = function(elm, name) {
	/// <summary>Renames the specified element to a new name and keep it's attributes and children.</summary>
	/// <param name="elm" type="Element" domElement="true">Element to rename.</param>
	/// <param name="name" type="String">Name of the new element.</param>
	/// <returns type="Object">New element or the old element if it needed renaming.</returns>
}

tinymce.dom.DOMUtils.prototype.findCommonAncestor = function(a, b) {
	/// <summary>Find the common ancestor of two elements.</summary>
	/// <param name="a" type="Element" domElement="true">Element to find common ancestor of.</param>
	/// <param name="b" type="Element" domElement="true">Element to find common ancestor of.</param>
	/// <returns type="Element" domElement="true">Common ancestor element of the two input elements.</returns>
}

tinymce.dom.DOMUtils.prototype.toHex = function(s) {
	/// <summary>Parses the specified RGB color value and returns a hex version of that color.</summary>
	/// <param name="s" type="String">RGB string value like rgb(1,2,3)</param>
	/// <returns type="String">Hex version of that RGB value like #FF00FF.</returns>
}

tinymce.dom.DOMUtils.prototype.getClasses = function() {
	/// <summary>Returns a array of all single CSS classes in the document.</summary>
	/// <returns type="Array">Array with class objects each object has a class field might be other fields in the future.</returns>
}

tinymce.dom.DOMUtils.prototype.run = function(Element, f, s) {
	/// <summary>Executes the specified function on the element by id or dom element node or array of elements/id.</summary>
	/// <param name="Element" type="">ID or DOM element object or array with ids or elements.</param>
	/// <param name="f" type="function">Function to execute for each item.</param>
	/// <param name="s" type="Object">Optional scope to execute the function in.</param>
	/// <returns type="">Single object or array with objects depending on multiple input or not.</returns>
}

tinymce.dom.DOMUtils.prototype.getAttribs = function(n) {
	/// <summary>Returns an NodeList with attributes for the element.</summary>
	/// <param name="n" type="">Element node or string id to get attributes from.</param>
	/// <returns type="NodeList">NodeList with attributes.</returns>
}

tinymce.dom.DOMUtils.prototype.isEmpty = function(elements) {
	/// <summary>Returns true/false if the specified node is to be considered empty or not.</summary>
	/// <param name="elements" type="Object">Optional name/value object with elements that are automatically treated as non empty elements.</param>
	/// <returns type="Boolean">true/false if the node is empty or not.</returns>
}

tinymce.dom.DOMUtils.prototype.destroy = function() {
	/// <summary>Destroys all internal references to the DOM to solve IE leak issues.</summary>
}

tinymce.dom.DOMUtils.prototype.createRng = function() {
	/// <summary>Created a new DOM Range object.</summary>
	/// <returns type="DOMRange">DOM Range object.</returns>
}

tinymce.dom.DOMUtils.prototype.split = function(pe, e, re) {
	/// <summary>Splits an element into two new elements and places the specified split element or element between the new ones.</summary>
	/// <param name="pe" type="Element" domElement="true">Parent element to split.</param>
	/// <param name="e" type="Element" domElement="true">Element to split at.</param>
	/// <param name="re" type="Element" domElement="true">Optional replacement element to replace the split element by.</param>
	/// <returns type="Element" domElement="true">Returns the split element or the replacement element if that is specified.</returns>
}

tinymce.dom.DOMUtils.prototype.bind = function(o, n, f, s) {
	/// <summary>Adds an event handler to the specified object.</summary>
	/// <param name="o" type="">Object or element id string to add event handler to or an array of elements/ids/documents.</param>
	/// <param name="n" type="String">Name of event handler to add for example: click.</param>
	/// <param name="f" type="function">Function to execute when the event occurs.</param>
	/// <param name="s" type="Object">Optional scope to execute the function in.</param>
	/// <returns type="function">Function callback handler the same as the one passed in.</returns>
}

tinymce.dom.DOMUtils.prototype.unbind = function(o, n, f) {
	/// <summary>Removes the specified event handler by name and function from a element or collection of elements.</summary>
	/// <param name="o" type="">Element ID string or HTML element or an array of elements or ids to remove handler from.</param>
	/// <param name="n" type="String">Event handler name like for example: "click"</param>
	/// <param name="f" type="function">Function to remove.</param>
	/// <returns type="">Bool state if true if the handler was removed or an array with states if multiple elements where passed in.</returns>
}

tinymce.dom.DOMUtils.prototype.fire = function(target, name, evt) {
	/// <summary>Fires the specified event name with object on target.</summary>
	/// <param name="target" type="">Target element or object to fire event on.</param>
	/// <param name="name" type="String">Name of the event to fire.</param>
	/// <param name="evt" type="Object">Event object to send.</param>
	/// <returns type="Event">Event object.</returns>
}

tinymce.dom.Element = function(id, settings) {
	/// <summary>Element class, this enables element blocking in IE.</summary>
	/// <param name="id" type="String">Element ID to bind/execute methods on.</param>
	/// <param name="settings" type="Object">Optional settings name/value collection.</param>
}

tinymce.dom.Element.prototype.on = function(n, f, s) {
	/// <summary>Adds a event handler to the element.</summary>
	/// <param name="n" type="String">Event name like for example "click".</param>
	/// <param name="f" type="function">Function to execute on the specified event.</param>
	/// <param name="s" type="Object">Optional scope to execute function on.</param>
	/// <returns type="function">Event handler function the same as the input function.</returns>
}

tinymce.dom.Element.prototype.getXY = function() {
	/// <summary>Returns the absolute X, Y cordinate of the element.</summary>
	/// <returns type="Object">Objext with x, y cordinate fields.</returns>
}

tinymce.dom.Element.prototype.getSize = function() {
	/// <summary>Returns the size of the element by a object with w and h fields.</summary>
	/// <returns type="Object">Object with element size with a w and h field.</returns>
}

tinymce.dom.Element.prototype.moveTo = function(x, y) {
	/// <summary>Moves the element to a specific absolute position.</summary>
	/// <param name="x" type="Number" integer="true">X cordinate of element position.</param>
	/// <param name="y" type="Number" integer="true">Y cordinate of element position.</param>
}

tinymce.dom.Element.prototype.moveBy = function(x, y) {
	/// <summary>Moves the element relative to the current position.</summary>
	/// <param name="x" type="Number" integer="true">Relative X cordinate of element position.</param>
	/// <param name="y" type="Number" integer="true">Relative Y cordinate of element position.</param>
}

tinymce.dom.Element.prototype.resizeTo = function(w, h) {
	/// <summary>Resizes the element to a specific size.</summary>
	/// <param name="w" type="Number" integer="true">New width of element.</param>
	/// <param name="h" type="Numner">New height of element.</param>
}

tinymce.dom.Element.prototype.resizeBy = function(w, h) {
	/// <summary>Resizes the element relative to the current sizeto a specific size.</summary>
	/// <param name="w" type="Number" integer="true">Relative width of element.</param>
	/// <param name="h" type="Numner">Relative height of element.</param>
}

tinymce.dom.Element.prototype.update = function(k) {
	/// <summary>Updates the element blocker in IE6 based on the style information of the element.</summary>
	/// <param name="k" type="String">Optional function key. Used internally.</param>
}

tinymce.dom.ScriptLoader = function() {
	/// <summary>This class handles asynchronous/synchronous loading of JavaScript files it will execute callbacks when various items get...</summary>
}

tinymce.dom.ScriptLoader.prototype.load = function(url, callback, scope) {
	/// <summary>Loads a specific script directly without adding it to the load queue.</summary>
	/// <param name="url" type="String">Absolute URL to script to add.</param>
	/// <param name="callback" type="function">Optional callback function to execute ones this script gets loaded.</param>
	/// <param name="scope" type="Object">Optional scope to execute callback in.</param>
}

tinymce.dom.ScriptLoader.prototype.isDone = function(url) {
	/// <summary>Returns true/false if a script has been loaded or not.</summary>
	/// <param name="url" type="String">URL to check for.</param>
	/// <returns type="Object">[Boolean} true/false if the URL is loaded.</returns>
}

tinymce.dom.ScriptLoader.prototype.markDone = function(u) {
	/// <summary>Marks a specific script to be loaded.</summary>
	/// <param name="u" type="string">Absolute URL to the script to mark as loaded.</param>
}

tinymce.dom.ScriptLoader.prototype.add = function(url, callback, scope) {
	/// <summary>Adds a specific script to the load queue of the script loader.</summary>
	/// <param name="url" type="String">Absolute URL to script to add.</param>
	/// <param name="callback" type="function">Optional callback function to execute ones this script gets loaded.</param>
	/// <param name="scope" type="Object">Optional scope to execute callback in.</param>
}

tinymce.dom.ScriptLoader.prototype.loadQueue = function(callback, scope) {
	/// <summary>Starts the loading of the queue.</summary>
	/// <param name="callback" type="function">Optional callback to execute when all queued items are loaded.</param>
	/// <param name="scope" type="Object">Optional scope to execute the callback in.</param>
}

tinymce.dom.ScriptLoader.prototype.loadScripts = function(scripts, callback, scope) {
	/// <summary>Loads the specified queue of files and executes the callback ones they are loaded.</summary>
	/// <param name="scripts" type="Array">Array of queue items to load.</param>
	/// <param name="callback" type="function">Optional callback to execute ones all items are loaded.</param>
	/// <param name="scope" type="Object">Optional scope to execute callback in.</param>
}

tinymce.dom.Selection = function(dom, win, serializer) {
	/// <summary>This class handles text and control selection it's an crossbrowser utility class.</summary>
	/// <param name="dom" type="tinymce.dom.DOMUtils">DOMUtils object reference.</param>
	/// <param name="win" type="Window">Window to bind the selection object to.</param>
	/// <param name="serializer" type="tinymce.dom.Serializer">DOM serialization class to use for getContent.</param>
	/// <field name="onBeforeSetContent" type="tinymce.util.Dispatcher">This event gets executed before contents is extracted from the selection. Selection object that fired the event.Contains things like the contents that will be returned.</field>
	/// <field name="onBeforeGetContent" type="tinymce.util.Dispatcher">This event gets executed before contents is inserted into selection. Selection object that fired the event.Contains things like the contents that will be inserted.</field>
	/// <field name="onSetContent" type="tinymce.util.Dispatcher">This event gets executed when contents is inserted into selection. Selection object that fired the event.Contains things like the contents that will be inserted.</field>
	/// <field name="onGetContent" type="tinymce.util.Dispatcher">This event gets executed when contents is extracted from the selection. Selection object that fired the event.Contains things like the contents that will be returned.</field>
}

tinymce.dom.Selection.prototype.getContent = function(s) {
	/// <summary>Returns the selected contents using the DOM serializer passed in to this class.</summary>
	/// <param name="s" type="Object">Optional settings class with for example output format text or html.</param>
	/// <returns type="String">Selected contents in for example HTML format.</returns>
}

tinymce.dom.Selection.prototype.setContent = function(content, args) {
	/// <summary>Sets the current selection to the specified content.</summary>
	/// <param name="content" type="String">HTML contents to set could also be other formats depending on settings.</param>
	/// <param name="args" type="Object">Optional settings object with for example data format.</param>
}

tinymce.dom.Selection.prototype.getStart = function() {
	/// <summary>Returns the start element of a selection range.</summary>
	/// <returns type="Element" domElement="true">Start element of selection range.</returns>
}

tinymce.dom.Selection.prototype.getEnd = function() {
	/// <summary>Returns the end element of a selection range.</summary>
	/// <returns type="Element" domElement="true">End element of selection range.</returns>
}

tinymce.dom.Selection.prototype.getBookmark = function(type, normalized) {
	/// <summary>Returns a bookmark location for the current selection.</summary>
	/// <param name="type" type="Number" integer="true">Optional state if the bookmark should be simple or not. Default is complex.</param>
	/// <param name="normalized" type="Boolean">Optional state that enables you to get a position that it would be after normalization.</param>
	/// <returns type="Object">Bookmark object, use moveToBookmark with this object to restore the selection.</returns>
}

tinymce.dom.Selection.prototype.moveToBookmark = function(bookmark) {
	/// <summary>Restores the selection to the specified bookmark.</summary>
	/// <param name="bookmark" type="Object">Bookmark to restore selection from.</param>
	/// <returns type="Boolean">true/false if it was successful or not.</returns>
}

tinymce.dom.Selection.prototype.select = function(node, content) {
	/// <summary>Selects the specified element.</summary>
	/// <param name="node" type="Element" domElement="true">HMTL DOM element to select.</param>
	/// <param name="content" type="Boolean">Optional bool state if the contents should be selected or not on non IE browser.</param>
	/// <returns type="Element" domElement="true">Selected element the same element as the one that got passed in.</returns>
}

tinymce.dom.Selection.prototype.isCollapsed = function() {
	/// <summary>Returns true/false if the selection range is collapsed or not.</summary>
	/// <returns type="Boolean">true/false state if the selection range is collapsed or not. Collapsed means if it's a caret or a larger selection.</returns>
}

tinymce.dom.Selection.prototype.collapse = function(to_start) {
	/// <summary>Collapse the selection to start or end of range.</summary>
	/// <param name="to_start" type="Boolean">Optional boolean state if to collapse to end or not. Defaults to start.</param>
}

tinymce.dom.Selection.prototype.getSel = function() {
	/// <summary>Returns the browsers internal selection object.</summary>
	/// <returns type="Selection">Internal browser selection object.</returns>
}

tinymce.dom.Selection.prototype.getRng = function(w3c) {
	/// <summary>Returns the browsers internal range object.</summary>
	/// <param name="w3c" type="Boolean">Forces a compatible W3C range on IE.</param>
	/// <returns type="Range">Internal browser range object.</returns>
}

tinymce.dom.Selection.prototype.setRng = function(r) {
	/// <summary>Changes the selection to the specified DOM range.</summary>
	/// <param name="r" type="Range">Range to select.</param>
}

tinymce.dom.Selection.prototype.setNode = function(n) {
	/// <summary>Sets the current selection to the specified DOM element.</summary>
	/// <param name="n" type="Element" domElement="true">Element to set as the contents of the selection.</param>
	/// <returns type="Element" domElement="true">Returns the element that got passed in.</returns>
}

tinymce.dom.Selection.prototype.getNode = function() {
	/// <summary>Returns the currently selected element or the common ancestor element for both start and end of the selection.</summary>
	/// <returns type="Element" domElement="true">Currently selected element or common ancestor element.</returns>
}

tinymce.dom.Serializer = function(settings, dom, schema) {
	/// <summary>This class is used to serialize DOM trees into a string.</summary>
	/// <param name="settings" type="Object">Serializer settings object.</param>
	/// <param name="dom" type="tinymce.dom.DOMUtils">DOMUtils instance reference.</param>
	/// <param name="schema" type="tinymce.html.Schema">Optional schema reference.</param>
	/// <field name="onPreProcess" type="tinymce.util.Dispatcher">This event gets executed before a HTML fragment gets serialized into a HTML string. This event enables you to do modifications to the DOM before the serialization occurs. It's important to know that the element that is getting serialized is cloned so it's not inside a document. object/Serializer instance that is serializing an element.Object containing things like the current node.// Adds an observer to the onPreProcess event serializer.onPreProcess.add(function(se, o) {     // Add a class to each paragraph     se.dom.addClass(se.dom.select('p', o.node), 'myclass'); });</field>
	/// <field name="onPreProcess" type="tinymce.util.Dispatcher">This event gets executed after a HTML fragment has been serialized into a HTML string. This event enables you to do modifications to the HTML string like regexp replaces etc. object/Serializer instance that is serializing an element.Object containing things like the current contents.// Adds an observer to the onPostProcess event serializer.onPostProcess.add(function(se, o) {    // Remove all paragraphs and replace with BR    o.content = o.content.replace(/<p[^>]+>|<p>/g, '');    o.content = o.content.replace(/<\/p>/g, '<br />'); });</field>
	/// <field name="onPreProcess" type="tinymce.util.Dispatcher">Fires when the Serializer does a preProcess on the contents. Editor instance.PreProcess object.DOM node for the item being serialized.The specified output format normally "html".Is true if the process is on a getContent operation.Is true if the process is on a setContent operation.Is true if the process is on a cleanup operation.</field>
	/// <field name="onPostProcess" type="tinymce.util.Dispatcher">Fires when the Serializer does a postProcess on the contents. Editor instance.PreProcess object.</field>
}

tinymce.dom.Serializer.prototype.addNodeFilter = function(callback) {
	/// <summary>Adds a node filter function to the parser used by the serializer, the parser will collect the specified nodes by name an...</summary>
	/// <param name="callback" type="function">Callback function to execute once it has collected nodes.</param>
}

tinymce.dom.Serializer.prototype.addAttributeFilter = function(callback) {
	/// <summary>Adds a attribute filter function to the parser used by the serializer, the parser will collect nodes that has the specif...</summary>
	/// <param name="callback" type="function">Callback function to execute once it has collected nodes.</param>
}

tinymce.dom.Serializer.prototype.serialize = function(node, args) {
	/// <summary>Serializes the specified browser DOM node into a HTML string.</summary>
	/// <param name="node" type="DOMNode">DOM node to serialize.</param>
	/// <param name="args" type="Object">Arguments option that gets passed to event handlers.</param>
}

tinymce.dom.Serializer.prototype.addRules = function(rules) {
	/// <summary>Adds valid elements rules to the serializers schema instance this enables you to specify things like what elements shoul...</summary>
	/// <param name="rules" type="String">Valid elements rules string to add to schema.</param>
}

tinymce.dom.Serializer.prototype.setRules = function(rules) {
	/// <summary>Sets the valid elements rules to the serializers schema instance this enables you to specify things like what elements s...</summary>
	/// <param name="rules" type="String">Valid elements rules string.</param>
}

tinymce.html.DomParser = function(settings, schema) {
	/// <summary>This class parses HTML code into a DOM like structure of nodes it will remove redundant whitespace and make sure that th...</summary>
	/// <param name="settings" type="Object">Name/value collection of settings. comment, cdata, text, start and end are callbacks.</param>
	/// <param name="schema" type="tinymce.html.Schema">HTML Schema class to use when parsing.</param>
}

tinymce.html.DomParser.prototype.addNodeFilter = function(callback) {
	/// <summary>Adds a node filter function to the parser, the parser will collect the specified nodes by name and then execute the call...</summary>
	/// <param name="callback" type="function">Callback function to execute once it has collected nodes.</param>
}

tinymce.html.DomParser.prototype.addAttributeFilter = function(callback) {
	/// <summary>Adds a attribute filter function to the parser, the parser will collect nodes that has the specified attributes and then...</summary>
	/// <param name="callback" type="function">Callback function to execute once it has collected nodes.</param>
}

tinymce.html.DomParser.prototype.parse = function(html, args) {
	/// <summary>Parses the specified HTML string into a DOM like node tree and returns the result.</summary>
	/// <param name="html" type="String">Html string to sax parse.</param>
	/// <param name="args" type="Object">Optional args object that gets passed to all filter functions.</param>
	/// <returns type="tinymce.html.Node">Root node containing the tree.</returns>
}

tinymce.html.SaxParser = function(settings, schema) {
	/// <summary>This class parses HTML code using pure JavaScript and executes various events for each item it finds.</summary>
	/// <param name="settings" type="Object">Name/value collection of settings. comment, cdata, text, start and end are callbacks.</param>
	/// <param name="schema" type="tinymce.html.Schema">HTML Schema class to use when parsing.</param>
}

tinymce.html.SaxParser.encodeRaw = function(text, attr) {
	/// <summary>Encodes the specified string using raw entities.</summary>
	/// <param name="text" type="String">Text to encode.</param>
	/// <param name="attr" type="Boolean">Optional flag to specify if the text is attribute contents.</param>
	/// <returns type="String">Entity encoded text.</returns>
}

tinymce.html.SaxParser.encodeAllRaw = function(text) {
	/// <summary>Encoded the specified text with both the attributes and text entities.</summary>
	/// <param name="text" type="String">Text to encode.</param>
	/// <returns type="String">Entity encoded text.</returns>
}

tinymce.html.SaxParser.encodeNumeric = function(text, attr) {
	/// <summary>Encodes the specified string using numeric entities.</summary>
	/// <param name="text" type="String">Text to encode.</param>
	/// <param name="attr" type="Boolean">Optional flag to specify if the text is attribute contents.</param>
	/// <returns type="String">Entity encoded text.</returns>
}

tinymce.html.SaxParser.encodeNamed = function(text, attr, entities) {
	/// <summary>Encodes the specified string using named entities.</summary>
	/// <param name="text" type="String">Text to encode.</param>
	/// <param name="attr" type="Boolean">Optional flag to specify if the text is attribute contents.</param>
	/// <param name="entities" type="Object">Optional parameter with entities to use.</param>
	/// <returns type="String">Entity encoded text.</returns>
}

tinymce.html.SaxParser.getEncodeFunc = function(name, entities) {
	/// <summary>Returns an encode function based on the name(s) and it's optional entities.</summary>
	/// <param name="name" type="String">Comma separated list of encoders for example named,numeric.</param>
	/// <param name="entities" type="String">Optional parameter with entities to use instead of the built in set.</param>
	/// <returns type="function">Encode function to be used.</returns>
}

tinymce.html.SaxParser.prototype.parse = function(html) {
	/// <summary>Parses the specified HTML string and executes the callbacks for each item it finds.</summary>
	/// <param name="html" type="String">Html string to sax parse.</param>
}

tinymce.html.Node = function(name, type) {
	/// <summary>This class is a minimalistic implementation of a DOM like node used by the DomParser class.</summary>
	/// <param name="name" type="String">Name of the node type.</param>
	/// <param name="type" type="Number" integer="true">Numeric type representing the node.</param>
}

tinymce.html.Node.prototype.replace = function(node) {
	/// <summary>Replaces the current node with the specified one.</summary>
	/// <param name="node" type="tinymce.html.Node">Node to replace the current node with.</param>
	/// <returns type="tinymce.html.Node">The old node that got replaced.</returns>
}

tinymce.html.Node.prototype.attr = function(name, value) {
	/// <summary>Gets/sets or removes an attribute by name.</summary>
	/// <param name="name" type="String">Attribute name to set or get.</param>
	/// <param name="value" type="String">Optional value to set.</param>
	/// <returns type="">String or undefined on a get operation or the current node on a set operation.</returns>
}

tinymce.html.Node.prototype.clone = function() {
	/// <summary>Does a shallow clones the node into a new node.</summary>
	/// <returns type="tinymce.html.Node">New copy of the original node.</returns>
}

tinymce.html.Node.prototype.wrap = function() {
	/// <summary>Wraps the node in in another node.</summary>
}

tinymce.html.Node.prototype.unwrap = function() {
	/// <summary>Unwraps the node in other words it removes the node but keeps the children.</summary>
}

tinymce.html.Node.prototype.remove = function() {
	/// <summary>Removes the node from it's parent.</summary>
	/// <returns type="tinymce.html.Node">Current node that got removed.</returns>
}

tinymce.html.Node.prototype.append = function(node) {
	/// <summary>Appends a new node as a child of the current node.</summary>
	/// <param name="node" type="tinymce.html.Node">Node to append as a child of the current one.</param>
	/// <returns type="tinymce.html.Node">The node that got appended.</returns>
}

tinymce.html.Node.prototype.insert = function(node, ref_node, before) {
	/// <summary>Inserts a node at a specific position as a child of the current node.</summary>
	/// <param name="node" type="tinymce.html.Node">Node to insert as a child of the current node.</param>
	/// <param name="ref_node" type="tinymce.html.Node">Reference node to set node before/after.</param>
	/// <param name="before" type="Boolean">Optional state to insert the node before the reference node.</param>
	/// <returns type="tinymce.html.Node">The node that got inserted.</returns>
}

tinymce.html.Node.prototype.getAll = function(name) {
	/// <summary>Get all children by name.</summary>
	/// <param name="name" type="String">Name of the child nodes to collect.</param>
	/// <returns type="Array">Array with child nodes matchin the specified name.</returns>
}

tinymce.html.Node.prototype.empty = function() {
	/// <summary>Removes all children of the current node.</summary>
	/// <returns type="tinymce.html.Node">The current node that got cleared.</returns>
}

tinymce.html.Node.prototype.isEmpty = function(elements) {
	/// <summary>Returns true/false if the node is to be considered empty or not.</summary>
	/// <param name="elements" type="Object">Name/value object with elements that are automatically treated as non empty elements.</param>
	/// <returns type="Boolean">true/false if the node is empty or not.</returns>
}

tinymce.html.Node.prototype.walk = function(prev) {
	/// <summary>Walks to the next or previous node and returns that node or null if it wasn't found.</summary>
	/// <param name="prev" type="Boolean">Optional previous node state defaults to false.</param>
	/// <returns type="tinymce.html.Node">Node that is next to or previous of the current node.</returns>
}

tinymce.html.Node.create = function(name, attrs) {
	/// <summary>Creates a node of a specific type.</summary>
	/// <param name="name" type="String">Name of the node type to create for example "b" or "#text".</param>
	/// <param name="attrs" type="Object">Name/value collection of attributes that will be applied to elements.</param>
}

tinymce.html.Schema = function(settings) {
	/// <summary>Schema validator class.</summary>
	/// <param name="settings" type="Object">Name/value settings object.</param>
}

tinymce.html.Schema.prototype.getBoolAttrs = function() {
	/// <summary>Returns a map with boolean attributes.</summary>
	/// <returns type="Object">Name/value lookup map for boolean attributes.</returns>
}

tinymce.html.Schema.prototype.getBoolAttrs = function() {
	/// <summary>Returns a map with block elements.</summary>
	/// <returns type="Object">Name/value lookup map for block elements.</returns>
}

tinymce.html.Schema.prototype.getShortEndedElements = function() {
	/// <summary>Returns a map with short ended elements such as BR or IMG.</summary>
	/// <returns type="Object">Name/value lookup map for short ended elements.</returns>
}

tinymce.html.Schema.prototype.getSelfClosingElements = function() {
	/// <summary>Returns a map with self closing tags such as .</summary>
	/// <returns type="Object">Name/value lookup map for self closing tags elements.</returns>
}

tinymce.html.Schema.prototype.getNonEmptyElements = function() {
	/// <summary>Returns a map with elements that should be treated as contents regardless if it has text content in them or not such as ...</summary>
	/// <returns type="Object">Name/value lookup map for non empty elements.</returns>
}

tinymce.html.Schema.prototype.getWhiteSpaceElements = function() {
	/// <summary>Returns a map with elements where white space is to be preserved like PRE or SCRIPT.</summary>
	/// <returns type="Object">Name/value lookup map for white space elements.</returns>
}

tinymce.html.Schema.prototype.isValidChild = function(name, child) {
	/// <summary>Returns true/false if the specified element and it's child is valid or not according to the schema.</summary>
	/// <param name="name" type="String">Element name to check for.</param>
	/// <param name="child" type="String">Element child to verify.</param>
	/// <returns type="Boolean">True/false if the element is a valid child of the specified parent.</returns>
}

tinymce.html.Schema.prototype.getElementRule = function(name) {
	/// <summary>Returns true/false if the specified element is valid or not according to the schema.</summary>
	/// <param name="name" type="String">Element name to check for.</param>
	/// <returns type="Object">Element object or undefined if the element isn't valid.</returns>
}

tinymce.html.Schema.prototype.getCustomElements = function() {
	/// <summary>Returns an map object of all custom elements.</summary>
	/// <returns type="Object">Name/value map object of all custom elements.</returns>
}

tinymce.html.Schema.prototype.addValidElements = function(valid_elements) {
	/// <summary>Parses a valid elements string and adds it to the schema.</summary>
	/// <param name="valid_elements" type="String">String in the valid elements format to be parsed.</param>
}

tinymce.html.Schema.prototype.setValidElements = function(valid_elements) {
	/// <summary>Parses a valid elements string and sets it to the schema.</summary>
	/// <param name="valid_elements" type="String">String in the valid elements format to be parsed.</param>
}

tinymce.html.Schema.prototype.addCustomElements = function(custom_elements) {
	/// <summary>Adds custom non HTML elements to the schema.</summary>
	/// <param name="custom_elements" type="String">Comma separated list of custom elements to add.</param>
}

tinymce.html.Schema.prototype.addValidChildren = function(valid_children) {
	/// <summary>Parses a valid children string and adds them to the schema structure.</summary>
	/// <param name="valid_children" type="String">Valid children elements string to parse</param>
}

tinymce.html.Serializer = function(settings, schema) {
	/// <summary>This class is used to serialize down the DOM tree into a string using a Writer instance.</summary>
	/// <param name="settings" type="Object">Name/value settings object.</param>
	/// <param name="schema" type="tinymce.html.Schema">Schema instance to use.</param>
}

tinymce.html.Serializer.prototype.serialize = function(node) {
	/// <summary>Serializes the specified node into a string.</summary>
	/// <param name="node" type="tinymce.html.Node">Node instance to serialize.</param>
	/// <returns type="String">String with HTML based on DOM tree.</returns>
}

tinymce.html.Styles = function() {
	/// <summary>This class is used to parse CSS styles it also compresses styles to reduce the output size.</summary>
}

tinymce.html.Styles.prototype.toHex = function(color) {
	/// <summary>Parses the specified RGB color value and returns a hex version of that color.</summary>
	/// <param name="color" type="String">RGB string value like rgb(1,2,3)</param>
	/// <returns type="String">Hex version of that RGB value like #FF00FF.</returns>
}

tinymce.html.Styles.prototype.parse = function(css) {
	/// <summary>Parses the specified style value into an object collection.</summary>
	/// <param name="css" type="String">Style value to parse for example: border:1px solid red;.</param>
	/// <returns type="Object">Object representation of that style like {border : '1px solid red'}</returns>
}

tinymce.html.Styles.prototype.serialize = function(styles, element_name) {
	/// <summary>Serializes the specified style object into a string.</summary>
	/// <param name="styles" type="Object">Object to serialize as string for example: {border : '1px solid red'}</param>
	/// <param name="element_name" type="String">Optional element name, if specified only the styles that matches the schema will be serialized.</param>
	/// <returns type="String">String representation of the style object for example: border: 1px solid red.</returns>
}

tinymce.html.Writer = function(settings) {
	/// <summary>This class is used to write HTML tags out it can be used with the Serializer or the SaxParser.</summary>
	/// <param name="settings" type="Object">Name/value settings object.</param>
}

tinymce.html.Writer.prototype.start = function(name, attrs, empty) {
	/// <summary>Writes the a start element such as .</summary>
	/// <param name="name" type="String">Name of the element.</param>
	/// <param name="attrs" type="Array">Optional attribute array or undefined if it hasn't any.</param>
	/// <param name="empty" type="Boolean">Optional empty state if the tag should end like <br />.</param>
}

tinymce.html.Writer.prototype.end = function(name) {
	/// <summary>Writes the a end element such as .</summary>
	/// <param name="name" type="String">Name of the element.</param>
}

tinymce.html.Writer.prototype.text = function(text, raw) {
	/// <summary>Writes a text node.</summary>
	/// <param name="text" type="String">String to write out.</param>
	/// <param name="raw" type="Boolean">Optional raw state if true the contents wont get encoded.</param>
}

tinymce.html.Writer.prototype.cdata = function(text) {
	/// <summary>Writes a cdata node such as .</summary>
	/// <param name="text" type="String">String to write out inside the cdata.</param>
}

tinymce.html.Writer.prototype.cdata = function(text) {
	/// <summary>Writes a comment node such as .</summary>
	/// <param name="text" type="String">String to write out inside the comment.</param>
}

tinymce.html.Writer.prototype.pi = function(name, text) {
	/// <summary>Writes a PI node such as .</summary>
	/// <param name="name" type="String">Name of the pi.</param>
	/// <param name="text" type="String">String to write out inside the pi.</param>
}

tinymce.html.Writer.prototype.doctype = function(text) {
	/// <summary>Writes a doctype node such as .</summary>
	/// <param name="text" type="String">String to write out inside the doctype.</param>
}

tinymce.html.Writer.prototype.reset = function() {
	/// <summary>Resets the internal buffer if one wants to reuse the writer.</summary>
}

tinymce.html.Writer.prototype.getContent = function() {
	/// <summary>Returns the contents that got serialized.</summary>
	/// <returns type="String">HTML contents that got written down.</returns>
}

tinymce.ui.Button = function(id, s, ed) {
	/// <summary>This class is used to create a UI button.</summary>
	/// <param name="id" type="String">Control id for the button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <param name="ed" type="Editor">Optional the editor instance this button is for.</param>
}

tinymce.ui.Button.prototype.renderHTML = function() {
	/// <summary>Renders the button as a HTML string.</summary>
	/// <returns type="String">HTML for the button control element.</returns>
}

tinymce.ui.Button.prototype.postRender = function() {
	/// <summary>Post render handler.</summary>
}

tinymce.ui.Button.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Button.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton = function(id, s, ed) {
	/// <summary>This class is used to create UI color split button.</summary>
	/// <param name="id" type="String">Control id for the color split button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <param name="ed" type="Editor">The editor instance this button is for.</param>
	/// <field name="settings" type="Object">Settings object.</field>
	/// <field name="value" type="String">Current color value.</field>
	/// <field name="onShowMenu" type="tinymce.util.Dispatcher">Fires when the menu is shown.</field>
	/// <field name="onHideMenu" type="tinymce.util.Dispatcher">Fires when the menu is hidden.</field>
}

tinymce.ui.ColorSplitButton.prototype.showMenu = function() {
	/// <summary>Shows the color menu.</summary>
}

tinymce.ui.ColorSplitButton.prototype.hideMenu = function(e) {
	/// <summary>Hides the color menu.</summary>
	/// <param name="e" type="Event">Optional event object.</param>
}

tinymce.ui.ColorSplitButton.prototype.renderMenu = function() {
	/// <summary>Renders the menu to the DOM.</summary>
}

tinymce.ui.ColorSplitButton.prototype.setColor = function(c) {
	/// <summary>Sets the current color for the control and hides the menu if it should be visible.</summary>
	/// <param name="c" type="String">Color code value in hex for example: #FF00FF</param>
}

tinymce.ui.ColorSplitButton.prototype.displayColor = function(c) {
	/// <summary>Change the currently selected color for the control.</summary>
	/// <param name="c" type="String">Color code value in hex for example: #FF00FF</param>
}

tinymce.ui.ColorSplitButton.prototype.postRender = function() {
	/// <summary>Post render event.</summary>
}

tinymce.ui.ColorSplitButton.prototype.destroy = function() {
	/// <summary>Destroys the control.</summary>
}

tinymce.ui.ColorSplitButton.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.ColorSplitButton.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Container = function(id, s) {
	/// <summary>This class is the base class for all container controls like toolbars.</summary>
	/// <param name="id" type="String">Control id to use for the container.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <field name="controls" type="Array">Array of controls added to the container.</field>
}

tinymce.ui.Container.prototype.add = function(c) {
	/// <summary>Adds a control to the collection of controls for the container.</summary>
	/// <param name="c" type="tinymce.ui.Control">Control instance to add to the container.</param>
	/// <returns type="tinymce.ui.Control">Same control instance that got passed in.</returns>
}

tinymce.ui.Container.prototype.get = function(n) {
	/// <summary>Returns a control by id from the containers collection.</summary>
	/// <param name="n" type="String">Id for the control to retrive.</param>
	/// <returns type="tinymce.ui.Control">Control instance by the specified name or undefined if it wasn't found.</returns>
}

tinymce.ui.Container.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Container.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.Control = function(id, s) {
	/// <summary>This class is the base class for all controls like buttons, toolbars, containers.</summary>
	/// <param name="id" type="String">Control id.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
}

tinymce.ui.Control.prototype.setDisabled = function(s) {
	/// <summary>Sets the disabled state for the control.</summary>
	/// <param name="s" type="Boolean">Boolean state if the control should be disabled or not.</param>
}

tinymce.ui.Control.prototype.isDisabled = function() {
	/// <summary>Returns true/false if the control is disabled or not.</summary>
	/// <returns type="Boolean">true/false if the control is disabled or not.</returns>
}

tinymce.ui.Control.prototype.setActive = function(s) {
	/// <summary>Sets the activated state for the control.</summary>
	/// <param name="s" type="Boolean">Boolean state if the control should be activated or not.</param>
}

tinymce.ui.Control.prototype.isActive = function() {
	/// <summary>Returns true/false if the control is disabled or not.</summary>
	/// <returns type="Boolean">true/false if the control is disabled or not.</returns>
}

tinymce.ui.Control.prototype.setState = function(c, s) {
	/// <summary>Sets the specified class state for the control.</summary>
	/// <param name="c" type="String">Class name to add/remove depending on state.</param>
	/// <param name="s" type="Boolean">True/false state if the class should be removed or added.</param>
}

tinymce.ui.Control.prototype.isRendered = function() {
	/// <summary>Returns true/false if the control has been rendered or not.</summary>
	/// <returns type="Boolean">State if the control has been rendered or not.</returns>
}

tinymce.ui.Control.prototype.renderHTML = function() {
	/// <summary>Renders the control as a HTML string.</summary>
	/// <returns type="String">HTML for the button control element.</returns>
}

tinymce.ui.Control.prototype.renderTo = function(n) {
	/// <summary>Renders the control to the specified container element.</summary>
	/// <param name="n" type="Element" domElement="true">HTML DOM element to add control to.</param>
}

tinymce.ui.Control.prototype.postRender = function() {
	/// <summary>Post render event.</summary>
}

tinymce.ui.Control.prototype.remove = function() {
	/// <summary>Removes the control.</summary>
}

tinymce.ui.Control.prototype.destroy = function() {
	/// <summary>Destroys the control will free any memory by removing event listeners etc.</summary>
}

tinymce.ui.DropMenu = function(id, s) {
	/// <summary>This class is used to create drop menus, a drop menu can be a context menu, or a menu for a list box or a menu bar.</summary>
	/// <param name="id" type="String">Button control id for the button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
}

tinymce.ui.DropMenu.prototype.createMenu = function(s) {
	/// <summary>Created a new sub menu for the drop menu control.</summary>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <returns type="tinymce.ui.DropMenu">New drop menu instance.</returns>
}

tinymce.ui.DropMenu.prototype.update = function() {
	/// <summary>Repaints the menu after new items have been added dynamically.</summary>
}

tinymce.ui.DropMenu.prototype.showMenu = function(x, y, px) {
	/// <summary>Displays the menu at the specified cordinate.</summary>
	/// <param name="x" type="Number" integer="true">Horizontal position of the menu.</param>
	/// <param name="y" type="Number" integer="true">Vertical position of the menu.</param>
	/// <param name="px" type="Numner">Optional parent X position used when menus are cascading.</param>
}

tinymce.ui.DropMenu.prototype.hideMenu = function() {
	/// <summary>Hides the displayed menu.</summary>
}

tinymce.ui.DropMenu.prototype.add = function(o) {
	/// <summary>Adds a new menu, menu item or sub classes of them to the drop menu.</summary>
	/// <param name="o" type="tinymce.ui.Control">Menu or menu item to add to the drop menu.</param>
	/// <returns type="tinymce.ui.Control">Same as the input control, the menu or menu item.</returns>
}

tinymce.ui.DropMenu.prototype.collapse = function(d) {
	/// <summary>Collapses the menu, this will hide the menu and all menu items.</summary>
	/// <param name="d" type="Boolean">Optional deep state. If this is set to true all children will be collapsed as well.</param>
}

tinymce.ui.DropMenu.prototype.remove = function(o) {
	/// <summary>Removes a specific sub menu or menu item from the drop menu.</summary>
	/// <param name="o" type="tinymce.ui.Control">Menu item or menu to remove from drop menu.</param>
	/// <returns type="tinymce.ui.Control">Control instance or null if it wasn't found.</returns>
}

tinymce.ui.DropMenu.prototype.destroy = function() {
	/// <summary>Destroys the menu.</summary>
}

tinymce.ui.DropMenu.prototype.renderNode = function() {
	/// <summary>Renders the specified menu node to the dom.</summary>
	/// <returns type="Element" domElement="true">Container element for the drop menu.</returns>
}

tinymce.ui.DropMenu.prototype.expand = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.isCollapsed = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.addSeparator = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.addMenu = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.hasMenus = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.removeAll = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.setSelected = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.isSelected = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.DropMenu.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.KeyboardNavigation = function(settings, dom) {
	/// <summary>This class provides basic keyboard navigation using the arrow keys to children of a component.</summary>
	/// <param name="settings" type="Object">the settings object to define how keyboard navigation works.</param>
	/// <param name="dom" type="DOMUtils">the DOMUtils instance to use.</param>
}

tinymce.ui.KeyboardNavigation.prototype.destroy = function() {
	/// <summary>Destroys the KeyboardNavigation and unbinds any focus/blur event handles it might have added.</summary>
}

tinymce.ui.ListBox = function(id, s, ed) {
	/// <summary>This class is used to create list boxes/select list.</summary>
	/// <param name="id" type="String">Control id for the list box.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <param name="ed" type="Editor">Optional the editor instance this button is for.</param>
	/// <field name="items" type="Array">Array of ListBox items.</field>
	/// <field name="onChange" type="tinymce.util.Dispatcher">Fires when the selection has been changed.</field>
	/// <field name="onPostRender" type="tinymce.util.Dispatcher">Fires after the element has been rendered to DOM.</field>
	/// <field name="onAdd" type="tinymce.util.Dispatcher">Fires when a new item is added.</field>
	/// <field name="onRenderMenu" type="tinymce.util.Dispatcher">Fires when the menu gets rendered.</field>
}

tinymce.ui.ListBox.prototype.select = function(va) {
	/// <summary>Selects a item/option by value.</summary>
	/// <param name="va" type="">Value to look for inside the list box or a function selector.</param>
}

tinymce.ui.ListBox.prototype.selectByIndex = function(idx) {
	/// <summary>Selects a item/option by index.</summary>
	/// <param name="idx" type="String">Index to select, pass -1 to select menu/title of select box.</param>
}

tinymce.ui.ListBox.prototype.add = function(n, v, o) {
	/// <summary>Adds a option item to the list box.</summary>
	/// <param name="n" type="String">Title for the new option.</param>
	/// <param name="v" type="String">Value for the new option.</param>
	/// <param name="o" type="Object">Optional object with settings like for example class.</param>
}

tinymce.ui.ListBox.prototype.getLength = function(Number) {
	/// <summary>Returns the number of items inside the list box.</summary>
	/// <param name="Number" type="Number" integer="true">of items inside the list box.</param>
}

tinymce.ui.ListBox.prototype.renderHTML = function() {
	/// <summary>Renders the list box as a HTML string.</summary>
	/// <returns type="String">HTML for the list box control element.</returns>
}

tinymce.ui.ListBox.prototype.showMenu = function() {
	/// <summary>Displays the drop menu with all items.</summary>
}

tinymce.ui.ListBox.prototype.hideMenu = function() {
	/// <summary>Hides the drop menu.</summary>
}

tinymce.ui.ListBox.prototype.renderMenu = function() {
	/// <summary>Renders the menu to the DOM.</summary>
}

tinymce.ui.ListBox.prototype.postRender = function() {
	/// <summary>Post render event.</summary>
}

tinymce.ui.ListBox.prototype.destroy = function() {
	/// <summary>Destroys the ListBox i.</summary>
}

tinymce.ui.ListBox.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.ListBox.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Menu = function(id, s) {
	/// <summary>This class is base class for all menu types like DropMenus etc.</summary>
	/// <param name="id" type="String">Button control id for the button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
}

tinymce.ui.Menu.prototype.expand = function(d) {
	/// <summary>Expands the menu, this will show them menu and all menu items.</summary>
	/// <param name="d" type="Boolean">Optional deep state. If this is set to true all children will be expanded as well.</param>
}

tinymce.ui.Menu.prototype.collapse = function(d) {
	/// <summary>Collapses the menu, this will hide the menu and all menu items.</summary>
	/// <param name="d" type="Boolean">Optional deep state. If this is set to true all children will be collapsed as well.</param>
}

tinymce.ui.Menu.prototype.isCollapsed = function() {
	/// <summary>Returns true/false if the menu has been collapsed or not.</summary>
	/// <returns type="Boolean">True/false state if the menu has been collapsed or not.</returns>
}

tinymce.ui.Menu.prototype.add = function(o) {
	/// <summary>Adds a new menu, menu item or sub classes of them to the drop menu.</summary>
	/// <param name="o" type="tinymce.ui.Control">Menu or menu item to add to the drop menu.</param>
	/// <returns type="tinymce.ui.Control">Same as the input control, the menu or menu item.</returns>
}

tinymce.ui.Menu.prototype.addSeparator = function() {
	/// <summary>Adds a menu separator between the menu items.</summary>
	/// <returns type="tinymce.ui.MenuItem">Menu item instance for the separator.</returns>
}

tinymce.ui.Menu.prototype.addMenu = function(o) {
	/// <summary>Adds a sub menu to the menu.</summary>
	/// <param name="o" type="Object">Menu control or a object with settings to be created into an control.</param>
	/// <returns type="tinymce.ui.Menu">Menu control instance passed in or created.</returns>
}

tinymce.ui.Menu.prototype.hasMenus = function() {
	/// <summary>Returns true/false if the menu has sub menus or not.</summary>
	/// <returns type="Boolean">True/false state if the menu has sub menues or not.</returns>
}

tinymce.ui.Menu.prototype.remove = function(o) {
	/// <summary>Removes a specific sub menu or menu item from the menu.</summary>
	/// <param name="o" type="tinymce.ui.Control">Menu item or menu to remove from menu.</param>
	/// <returns type="tinymce.ui.Control">Control instance or null if it wasn't found.</returns>
}

tinymce.ui.Menu.prototype.removeAll = function() {
	/// <summary>Removes all menu items and sub menu items from the menu.</summary>
}

tinymce.ui.Menu.prototype.createMenu = function(s) {
	/// <summary>Created a new sub menu for the menu control.</summary>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <returns type="tinymce.ui.Menu">New drop menu instance.</returns>
}

tinymce.ui.Menu.prototype.setSelected = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.isSelected = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.Menu.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton = function(id, s, ed) {
	/// <summary>This class is used to create a UI button.</summary>
	/// <param name="id" type="String">Control id for the split button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <param name="ed" type="Editor">Optional the editor instance this button is for.</param>
	/// <field name="onRenderMenu" type="tinymce.util.Dispatcher">Fires when the menu is rendered.</field>
}

tinymce.ui.MenuButton.prototype.showMenu = function() {
	/// <summary>Shows the menu.</summary>
}

tinymce.ui.MenuButton.prototype.renderMenu = function() {
	/// <summary>Renders the menu to the DOM.</summary>
}

tinymce.ui.MenuButton.prototype.hideMenu = function(e) {
	/// <summary>Hides the menu.</summary>
	/// <param name="e" type="Event">Optional event object.</param>
}

tinymce.ui.MenuButton.prototype.postRender = function() {
	/// <summary>Post render handler.</summary>
}

tinymce.ui.MenuButton.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.MenuButton.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem = function(id, s) {
	/// <summary>This class is base class for all menu item types like DropMenus items etc.</summary>
	/// <param name="id" type="String">Button control id for the button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
}

tinymce.ui.MenuItem.prototype.setSelected = function(s) {
	/// <summary>Sets the selected state for the control.</summary>
	/// <param name="s" type="Boolean">Boolean state if the control should be selected or not.</param>
}

tinymce.ui.MenuItem.prototype.isSelected = function() {
	/// <summary>Returns true/false if the control is selected or not.</summary>
	/// <returns type="Boolean">true/false if the control is selected or not.</returns>
}

tinymce.ui.MenuItem.prototype.postRender = function() {
	/// <summary>Post render handler.</summary>
}

tinymce.ui.MenuItem.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.renderHTML = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.MenuItem.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox = function(id, s) {
	/// <summary>This class is used to create list boxes/select list.</summary>
	/// <param name="id" type="String">Button control id for the button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <field name="items" type=""></field>
	/// <field name="onChange" type="tinymce.util.Dispatcher"></field>
	/// <field name="onPostRender" type="tinymce.util.Dispatcher"></field>
	/// <field name="onAdd" type="tinymce.util.Dispatcher"></field>
	/// <field name="onRenderMenu" type="tinymce.util.Dispatcher"></field>
}

tinymce.ui.NativeListBox.prototype.setDisabled = function(s) {
	/// <summary>Sets the disabled state for the control.</summary>
	/// <param name="s" type="Boolean">Boolean state if the control should be disabled or not.</param>
}

tinymce.ui.NativeListBox.prototype.isDisabled = function() {
	/// <summary>Returns true/false if the control is disabled or not.</summary>
	/// <returns type="Boolean">true/false if the control is disabled or not.</returns>
}

tinymce.ui.NativeListBox.prototype.select = function(va) {
	/// <summary>Selects a item/option by value.</summary>
	/// <param name="va" type="">Value to look for inside the list box or a function selector.</param>
}

tinymce.ui.NativeListBox.prototype.selectByIndex = function(idx) {
	/// <summary>Selects a item/option by index.</summary>
	/// <param name="idx" type="String">Index to select, pass -1 to select menu/title of select box.</param>
}

tinymce.ui.NativeListBox.prototype.add = function(n, v, o) {
	/// <summary>Adds a option item to the list box.</summary>
	/// <param name="n" type="String">Title for the new option.</param>
	/// <param name="v" type="String">Value for the new option.</param>
	/// <param name="o" type="Object">Optional object with settings like for example class.</param>
}

tinymce.ui.NativeListBox.prototype.getLength = function() {
	/// <summary>Executes the specified callback function for the menu item.</summary>
}

tinymce.ui.NativeListBox.prototype.renderHTML = function() {
	/// <summary>Renders the list box as a HTML string.</summary>
	/// <returns type="String">HTML for the list box control element.</returns>
}

tinymce.ui.NativeListBox.prototype.postRender = function() {
	/// <summary>Post render handler.</summary>
}

tinymce.ui.NativeListBox.prototype.showMenu = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.hideMenu = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.renderMenu = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.NativeListBox.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Separator = function(id, s) {
	/// <summary>This class is used to create vertical separator between other controls.</summary>
	/// <param name="id" type="String">Control id to use for the Separator.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
}

tinymce.ui.Separator.prototype.renderHTML = function() {
	/// <summary>Renders the separator as a HTML string.</summary>
	/// <returns type="String">HTML for the separator control element.</returns>
}

tinymce.ui.Separator.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Separator.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton = function(id, s, ed) {
	/// <summary>This class is used to create a split button.</summary>
	/// <param name="id" type="String">Control id for the split button.</param>
	/// <param name="s" type="Object">Optional name/value settings object.</param>
	/// <param name="ed" type="Editor">Optional the editor instance this button is for.</param>
}

tinymce.ui.SplitButton.prototype.renderHTML = function() {
	/// <summary>Renders the split button as a HTML string.</summary>
	/// <returns type="String">HTML for the split button control element.</returns>
}

tinymce.ui.SplitButton.prototype.postRender = function() {
	/// <summary>Post render handler.</summary>
}

tinymce.ui.SplitButton.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.SplitButton.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar = function() {
	/// <summary>This class is used to create toolbars a toolbar is a container for other controls like buttons etc.</summary>
	/// <field name="controls" type=""></field>
}

tinymce.ui.Toolbar.prototype.renderHTML = function() {
	/// <summary>Renders the toolbar as a HTML string.</summary>
	/// <returns type="String">HTML for the toolbar control.</returns>
}

tinymce.ui.Toolbar.prototype.add = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.get = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.Toolbar.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup = function() {
	/// <summary>This class is used to group a set of toolbars together and control the keyboard navigation and focus.</summary>
	/// <field name="controls" type=""></field>
}

tinymce.ui.ToolbarGroup.prototype.renderHTML = function() {
	/// <summary>Renders the toolbar group as a HTML string.</summary>
	/// <returns type="String">HTML for the toolbar control.</returns>
}

tinymce.ui.ToolbarGroup.prototype.add = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.get = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.setDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.isDisabled = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.setActive = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.isActive = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.setState = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.isRendered = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.renderTo = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.postRender = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.remove = function() {
	/// <summary></summary>
}

tinymce.ui.ToolbarGroup.prototype.destroy = function() {
	/// <summary></summary>
}

tinymce.util.Cookie = function() {
	/// <summary>This class contains simple cookie manangement functions.</summary>
}

tinymce.util.Cookie.getHash = function(n) {
	/// <summary>Parses the specified query string into an name/value object.</summary>
	/// <param name="n" type="String">String to parse into a n Hashtable object.</param>
	/// <returns type="Object">Name/Value object with items parsed from querystring.</returns>
}

tinymce.util.Cookie.setHash = function(n, v, e, p, d, s) {
	/// <summary>Sets a hashtable name/value object to a cookie.</summary>
	/// <param name="n" type="String">Name of the cookie.</param>
	/// <param name="v" type="Object">Hashtable object to set as cookie.</param>
	/// <param name="e" type="Date">Optional date object for the expiration of the cookie.</param>
	/// <param name="p" type="String">Optional path to restrict the cookie to.</param>
	/// <param name="d" type="String">Optional domain to restrict the cookie to.</param>
	/// <param name="s" type="String">Is the cookie secure or not.</param>
}

tinymce.util.Cookie.get = function(n) {
	/// <summary>Gets the raw data of a cookie by name.</summary>
	/// <param name="n" type="String">Name of cookie to retrive.</param>
	/// <returns type="String">Cookie data string.</returns>
}

tinymce.util.Cookie.set = function(n, v, e, p, d, s) {
	/// <summary>Sets a raw cookie string.</summary>
	/// <param name="n" type="String">Name of the cookie.</param>
	/// <param name="v" type="String">Raw cookie data.</param>
	/// <param name="e" type="Date">Optional date object for the expiration of the cookie.</param>
	/// <param name="p" type="String">Optional path to restrict the cookie to.</param>
	/// <param name="d" type="String">Optional domain to restrict the cookie to.</param>
	/// <param name="s" type="String">Is the cookie secure or not.</param>
}

tinymce.util.Cookie.remove = function(n, p) {
	/// <summary>Removes/deletes a cookie by name.</summary>
	/// <param name="n" type="String">Cookie name to remove/delete.</param>
	/// <param name="p" type="Strong">Optional path to remove the cookie from.</param>
}

tinymce.util.Dispatcher = function(s) {
	/// <summary>This class is used to dispatch event to observers/listeners.</summary>
	/// <param name="s" type="Object">Optional default execution scope for all observer functions.</param>
}

tinymce.util.Dispatcher.prototype.add = function(cb, s) {
	/// <summary>Add an observer function to be executed when a dispatch call is done.</summary>
	/// <param name="cb" type="function">Callback function to execute when a dispatch event occurs.</param>
	/// <param name="s" type="Object">Optional execution scope, defaults to the one specified in the class constructor.</param>
	/// <returns type="function">Returns the same function as the one passed on.</returns>
}

tinymce.util.Dispatcher.prototype.addToTop = function(cb, s) {
	/// <summary>Add an observer function to be executed to the top of the list of observers.</summary>
	/// <param name="cb" type="function">Callback function to execute when a dispatch event occurs.</param>
	/// <param name="s" type="Object">Optional execution scope, defaults to the one specified in the class constructor.</param>
	/// <returns type="function">Returns the same function as the one passed on.</returns>
}

tinymce.util.Dispatcher.prototype.remove = function(cb) {
	/// <summary>Removes an observer function.</summary>
	/// <param name="cb" type="function">Observer function to remove.</param>
	/// <returns type="function">The same function that got passed in or null if it wasn't found.</returns>
}

tinymce.util.Dispatcher.prototype.dispatch = function() {
	/// <summary>Dispatches an event to all observers/listeners.</summary>
	/// <param name="" type="Object">Any number of arguments to dispatch.</param>
	/// <returns type="Object">Last observer functions return value.</returns>
}

tinymce.util.JSON = function() {
	/// <summary>JSON parser and serializer class.</summary>
}

tinymce.util.JSON.serialize = function(obj, quote) {
	/// <summary>Serializes the specified object as a JSON string.</summary>
	/// <param name="obj" type="Object">Object to serialize as a JSON string.</param>
	/// <param name="quote" type="String">Optional quote string defaults to ".</param>
	/// <returns type="string">JSON string serialized from input.</returns>
}

tinymce.util.JSON.parse = function(s) {
	/// <summary>Unserializes/parses the specified JSON string into a object.</summary>
	/// <param name="s" type="string">JSON String to parse into a JavaScript object.</param>
	/// <returns type="Object">Object from input JSON string or undefined if it failed.</returns>
}

tinymce.util.JSONRequest = function(s) {
	/// <summary>This class enables you to use JSON-RPC to call backend methods.</summary>
	/// <param name="s" type="Object">Optional settings object.</param>
}

tinymce.util.JSONRequest.prototype.send = function(o) {
	/// <summary>Sends a JSON-RPC call.</summary>
	/// <param name="o" type="Object">Call object where there are three field id, method and params this object should also contain callbacks etc.</param>
}

tinymce.util.JSONRequest.sendRPC = function(o) {
	/// <summary>Simple helper function to send a JSON-RPC request without the need to initialize an object.</summary>
	/// <param name="o" type="Object">Call object where there are three field id, method and params this object should also contain callbacks etc.</param>
}

tinymce.util.URI = function(u, s) {
	/// <summary>This class handles parsing, modification and serialization of URI/URL strings.</summary>
	/// <param name="u" type="String">URI string to parse.</param>
	/// <param name="s" type="Object">Optional settings object.</param>
}

tinymce.util.URI.prototype.setPath = function(p) {
	/// <summary>Sets the internal path part of the URI.</summary>
	/// <param name="p" type="string">Path string to set.</param>
}

tinymce.util.URI.prototype.toRelative = function(u) {
	/// <summary>Converts the specified URI into a relative URI based on the current URI instance location.</summary>
	/// <param name="u" type="String">URI to convert into a relative path/URI.</param>
	/// <returns type="String">Relative URI from the point specified in the current URI instance.</returns>
}

tinymce.util.URI.prototype.toAbsolute = function(u, nh) {
	/// <summary>Converts the specified URI into a absolute URI based on the current URI instance location.</summary>
	/// <param name="u" type="String">URI to convert into a relative path/URI.</param>
	/// <param name="nh" type="Boolean">No host and protocol prefix.</param>
	/// <returns type="String">Absolute URI from the point specified in the current URI instance.</returns>
}

tinymce.util.URI.prototype.toRelPath = function(base, path) {
	/// <summary>Converts a absolute path into a relative path.</summary>
	/// <param name="base" type="String">Base point to convert the path from.</param>
	/// <param name="path" type="String">Absolute path to convert into a relative path.</param>
}

tinymce.util.URI.prototype.toAbsPath = function(base, path) {
	/// <summary>Converts a relative path into a absolute path.</summary>
	/// <param name="base" type="String">Base point to convert the path from.</param>
	/// <param name="path" type="String">Relative path to convert into an absolute path.</param>
}

tinymce.util.URI.prototype.getURI = function(nh) {
	/// <summary>Returns the full URI of the internal structure.</summary>
	/// <param name="nh" type="Boolean">Optional no host and protocol part. Defaults to false.</param>
}

tinymce.util.XHR = function() {
	/// <summary>This class enables you to send XMLHTTPRequests cross browser.</summary>
}

tinymce.util.XHR.send = function(o) {
	/// <summary>Sends a XMLHTTPRequest.</summary>
	/// <param name="o" type="Object">Object will target URL, callbacks and other info needed to make the request.</param>
}

tinymce.plugins.AutoSave = function() {
	/// <summary>This plugin adds auto-save capability to the TinyMCE text editor to rescue content inadvertently lost.</summary>
	/// <field name="onStoreDraft" type="tinymce.util.Dispatcher">This event gets fired when a draft is stored to local storage. Plugin instance sending the event.Draft object containing the HTML contents of the editor.</field>
	/// <field name="onStoreDraft" type="tinymce.util.Dispatcher">This event gets fired when a draft is restored from local storage. Plugin instance sending the event.Draft object containing the HTML contents of the editor.</field>
	/// <field name="onRemoveDraft" type="tinymce.util.Dispatcher">This event gets fired when a draft removed/expired. Plugin instance sending the event.Draft object containing the HTML contents of the editor.</field>
}

tinymce.plugins.AutoSave.prototype.init = function(ed, url) {
	/// <summary>Initializes the plugin, this will be executed after the plugin has been created.</summary>
	/// <param name="ed" type="tinymce.Editor">Editor instance that the plugin is initialized in.</param>
	/// <param name="url" type="string">Absolute URL to where the plugin is located.</param>
}

tinymce.plugins.AutoSave.prototype.getInfo = function() {
	/// <summary>Returns information about the plugin as a name/value array.</summary>
	/// <returns type="Object">Name/value array containing information about the plugin.</returns>
}

tinymce.plugins.AutoSave.prototype.getExpDate = function() {
	/// <summary>Returns an expiration date UTC string.</summary>
	/// <returns type="String">Expiration date UTC string.</returns>
}

tinymce.plugins.AutoSave.prototype.setupStorage = function() {
	/// <summary>This method will setup the storage engine.</summary>
}

tinymce.plugins.AutoSave.prototype.storeDraft = function() {
	/// <summary>This method will store the current contents in the the storage engine.</summary>
}

tinymce.plugins.AutoSave.prototype.restoreDraft = function() {
	/// <summary>This method will restore the contents from the storage engine back to the editor.</summary>
}

tinymce.plugins.AutoSave.prototype.hasDraft = function() {
	/// <summary>This method will return true/false if there is a local storage draft available.</summary>
	/// <returns type="boolean">true/false state if there is a local draft.</returns>
}

tinymce.plugins.AutoSave.prototype.removeDraft = function() {
	/// <summary>Removes the currently stored draft.</summary>
}

tinymce.plugins.ContextMenu = function() {
	/// <summary>This plugin a context menu to TinyMCE editor instances.</summary>
	/// <field name="onContextMenu" type="tinymce.util.Dispatcher">This event gets fired when the context menu is shown. Plugin instance sending the event.Drop down menu to fill with more items if needed.</field>
}

tinymce.plugins.ContextMenu.prototype.init = function(ed, url) {
	/// <summary>Initializes the plugin, this will be executed after the plugin has been created.</summary>
	/// <param name="ed" type="tinymce.Editor">Editor instance that the plugin is initialized in.</param>
	/// <param name="url" type="string">Absolute URL to where the plugin is located.</param>
}

tinymce.plugins.ContextMenu.prototype.getInfo = function() {
	/// <summary>Returns information about the plugin as a name/value array.</summary>
	/// <returns type="Object">Name/value array containing information about the plugin.</returns>
}

tinyMCEPopup = function() {
	/// <summary>TinyMCE popup/dialog helper class.</summary>
	/// <field name="onInit" type="tinymce.util.Dispatcher">Fires when the popup is initialized. Editor instance.// Alerts the selected contents when the dialog is loaded tinyMCEPopup.onInit.add(function(ed) {     alert(ed.selection.getContent()); });  // Executes the init method on page load in some object using the SomeObject scope tinyMCEPopup.onInit.add(SomeObject.init, SomeObject);</field>
}

tinyMCEPopup.init = function() {
	/// <summary>Initializes the popup this will be called automatically.</summary>
}

tinyMCEPopup.getWin = function() {
	/// <summary>Returns the reference to the parent window that opened the dialog.</summary>
	/// <returns type="Window">Reference to the parent window that opened the dialog.</returns>
}

tinyMCEPopup.getWindowArg = function(n, dv) {
	/// <summary>Returns a window argument/parameter by name.</summary>
	/// <param name="n" type="String">Name of the window argument to retrive.</param>
	/// <param name="dv" type="String">Optional default value to return.</param>
	/// <returns type="String">Argument value or default value if it wasn't found.</returns>
}

tinyMCEPopup.getParam = function(n, dv) {
	/// <summary>Returns a editor parameter/config option value.</summary>
	/// <param name="n" type="String">Name of the editor config option to retrive.</param>
	/// <param name="dv" type="String">Optional default value to return.</param>
	/// <returns type="String">Parameter value or default value if it wasn't found.</returns>
}

tinyMCEPopup.getLang = function(n, dv) {
	/// <summary>Returns a language item by key.</summary>
	/// <param name="n" type="String">Language item like mydialog.something.</param>
	/// <param name="dv" type="String">Optional default value to return.</param>
	/// <returns type="String">Language value for the item like "my string" or the default value if it wasn't found.</returns>
}

tinyMCEPopup.execCommand = function(cmd, ui, val, a) {
	/// <summary>Executed a command on editor that opened the dialog/popup.</summary>
	/// <param name="cmd" type="String">Command to execute.</param>
	/// <param name="ui" type="Boolean">Optional boolean value if the UI for the command should be presented or not.</param>
	/// <param name="val" type="Object">Optional value to pass with the comman like an URL.</param>
	/// <param name="a" type="Object">Optional arguments object.</param>
}

tinyMCEPopup.resizeToInnerSize = function() {
	/// <summary>Resizes the dialog to the inner size of the window.</summary>
}

tinyMCEPopup.executeOnLoad = function(s) {
	/// <summary>Will executed the specified string when the page has been loaded.</summary>
	/// <param name="s" type="String">String to evalutate on init.</param>
}

tinyMCEPopup.storeSelection = function() {
	/// <summary>Stores the current editor selection for later restoration.</summary>
}

tinyMCEPopup.restoreSelection = function() {
	/// <summary>Restores any stored selection.</summary>
}

tinyMCEPopup.requireLangPack = function() {
	/// <summary>Loads a specific dialog language pack.</summary>
}

tinyMCEPopup.pickColor = function(e, element_id) {
	/// <summary>Executes a color picker on the specified element id.</summary>
	/// <param name="e" type="DOMEvent">DOM event object.</param>
	/// <param name="element_id" type="string">Element id to be filled with the color value from the picker.</param>
}

tinyMCEPopup.openBrowser = function(element_id, type, option) {
	/// <summary>Opens a filebrowser/imagebrowser this will set the output value from the browser as a value on the specified element.</summary>
	/// <param name="element_id" type="string">Id of the element to set value in.</param>
	/// <param name="type" type="string">Type of browser to open image/file/flash.</param>
	/// <param name="option" type="string">Option name to get the file_broswer_callback function name from.</param>
}

tinyMCEPopup.confirm = function(t, cb, s) {
	/// <summary>Creates a confirm dialog.</summary>
	/// <param name="t" type="String">Title for the new confirm dialog.</param>
	/// <param name="cb" type="function">Callback function to be executed after the user has selected ok or cancel.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinyMCEPopup.alert = function(t, cb, s) {
	/// <summary>Creates a alert dialog.</summary>
	/// <param name="t" type="String">Title for the new alert dialog.</param>
	/// <param name="cb" type="function">Callback function to be executed after the user has selected ok.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinyMCEPopup.close = function() {
	/// <summary>Closes the current window.</summary>
}

// Namespaces
tinymce.EditorManager = new tinymce();
tinymce.DOM = new tinymce.dom.DOMUtils();
tinymce.baseURI = new tinymce.util.URI();
tinymce.editors = new Object();
tinymce.i18n = new Object();
tinymce.activeEditor = new tinymce.Editor();
tinymce.majorVersion = new String();
tinymce.minorVersion = new String();
tinymce.releaseDate = new String();
tinymce.isOpera = new Boolean();
tinymce.isWebKit = new Boolean();
tinymce.isIE = new Boolean();
tinymce.isIE6 = new Boolean();
tinymce.isIE7 = new Boolean();
tinymce.isIE8 = new Boolean();
tinymce.isIE9 = new Boolean();
tinymce.isGecko = new Boolean();
tinymce.isMac = new Boolean();
tinymce.isAir = new Boolean();
tinymce.isIDevice = new Boolean();
tinymce.isIOS5 = new Boolean();
tinymce.onAddEditor = new tinymce.util.Dispatcher();
tinymce.onRemoveEditor = new tinymce.util.Dispatcher();
tinymce.prototype.init = function(s) {
	/// <summary>Initializes a set of editors.</summary>
	/// <param name="s" type="Object">Settings object to be passed to each editor instance.</param>
}

tinymce.prototype.get = function(id) {
	/// <summary>Returns a editor instance by id.</summary>
	/// <param name="id" type="">Editor instance id or index to return.</param>
	/// <returns type="tinymce.Editor">Editor instance to return.</returns>
}

tinymce.prototype.getInstanceById = function(id) {
	/// <summary>Returns a editor instance by id.</summary>
	/// <param name="id" type="String">Editor instance id to return.</param>
	/// <returns type="tinymce.Editor">Editor instance to return.</returns>
}

tinymce.prototype.add = function(editor) {
	/// <summary>Adds an editor instance to the editor collection.</summary>
	/// <param name="editor" type="tinymce.Editor">Editor instance to add to the collection.</param>
	/// <returns type="tinymce.Editor">The same instance that got passed in.</returns>
}

tinymce.prototype.remove = function(e) {
	/// <summary>Removes a editor instance from the collection.</summary>
	/// <param name="e" type="tinymce.Editor">Editor instance to remove.</param>
	/// <returns type="tinymce.Editor">The editor that got passed in will be return if it was found otherwise null.</returns>
}

tinymce.prototype.execCommand = function(c, u, v) {
	/// <summary>Executes a specific command on the currently active editor.</summary>
	/// <param name="c" type="String">Command to perform for example Bold.</param>
	/// <param name="u" type="Boolean">Optional boolean state if a UI should be presented for the command or not.</param>
	/// <param name="v" type="String">Optional value parameter like for example an URL to a link.</param>
	/// <returns type="Boolean">true/false if the command was executed or not.</returns>
}

tinymce.prototype.execInstanceCommand = function(id, c, u, v) {
	/// <summary>Executes a command on a specific editor by id.</summary>
	/// <param name="id" type="String">Editor id to perform the command on.</param>
	/// <param name="c" type="String">Command to perform for example Bold.</param>
	/// <param name="u" type="Boolean">Optional boolean state if a UI should be presented for the command or not.</param>
	/// <param name="v" type="String">Optional value parameter like for example an URL to a link.</param>
	/// <returns type="Boolean">true/false if the command was executed or not.</returns>
}

tinymce.prototype.triggerSave = function() {
	/// <summary>Calls the save method on all editor instances in the collection.</summary>
}

tinymce.prototype.addI18n = function(p, o) {
	/// <summary>Adds a language pack, this gets called by the loaded language files like en.</summary>
	/// <param name="p" type="String">Prefix for the language items. For example en.myplugin</param>
	/// <param name="o" type="Object">Name/Value collection with items to add to the language group.</param>
}

tinymce.is = function(o, t) {
	/// <summary>Checks if a object is of a specific type for example an array.</summary>
	/// <param name="o" type="Object">Object to check type of.</param>
	/// <param name="t" type="string">Optional type to check for.</param>
	/// <returns type="Boolean">true/false if the object is of the specified type.</returns>
}

tinymce.makeMap = function(items, delim, map) {
	/// <summary>Makes a name/object map out of an array with names.</summary>
	/// <param name="items" type="">Items to make map out of.</param>
	/// <param name="delim" type="String">Optional delimiter to split string by.</param>
	/// <param name="map" type="Object">Optional map to add items to.</param>
	/// <returns type="Object">Name/value map of items.</returns>
}

tinymce.each = function(o, cb, s) {
	/// <summary>Performs an iteration of all items in a collection such as an object or array.</summary>
	/// <param name="o" type="Object">Collection to iterate.</param>
	/// <param name="cb" type="function">Callback function to execute for each item.</param>
	/// <param name="s" type="Object">Optional scope to execute the callback in.</param>
}

tinymce.map = function(a, f) {
	/// <summary>Creates a new array by the return value of each iteration function call.</summary>
	/// <param name="a" type="Array">Array of items to iterate.</param>
	/// <param name="f" type="function">Function to call for each item. It's return value will be the new value.</param>
	/// <returns type="Array">Array with new values based on function return values.</returns>
}

tinymce.grep = function(a, f) {
	/// <summary>Filters out items from the input array by calling the specified function for each item.</summary>
	/// <param name="a" type="Array">Array of items to loop though.</param>
	/// <param name="f" type="function">Function to call for each item. Include/exclude depends on it's return value.</param>
	/// <returns type="Array">New array with values imported and filtered based in input.</returns>
}

tinymce.inArray = function(a, v) {
	/// <summary>Returns the index of a value in an array, this method will return -1 if the item wasn't found.</summary>
	/// <param name="a" type="Array">Array/Object to search for value in.</param>
	/// <param name="v" type="Object">Value to check for inside the array.</param>
	/// <returns type="">Index of item inside the array inside an object. Or -1 if it wasn't found.</returns>
}

tinymce.extend = function(o, en) {
	/// <summary>Extends an object with the specified other object(s).</summary>
	/// <param name="o" type="Object">Object to extend with new items.</param>
	/// <param name="en" type="Object">Object(s) to extend the specified object with.</param>
	/// <returns type="Object">o New extended object, same reference as the input object.</returns>
}

tinymce.trim = function(s) {
	/// <summary>Removes whitespace from the beginning and end of a string.</summary>
	/// <param name="s" type="String">String to remove whitespace from.</param>
	/// <returns type="String">New string with removed whitespace.</returns>
}

tinymce.create = function(s, p, root) {
	/// <summary>Creates a class, subclass or static singleton.</summary>
	/// <param name="s" type="String">Class name, inheritage and prefix.</param>
	/// <param name="p" type="Object">Collection of methods to add to the class.</param>
	/// <param name="root" type="Object">Optional root object defaults to the global window object.</param>
}

tinymce.walk = function(o, f, n, s) {
	/// <summary>Executed the specified function for each item in a object tree.</summary>
	/// <param name="o" type="Object">Object tree to walk though.</param>
	/// <param name="f" type="function">Function to call for each item.</param>
	/// <param name="n" type="String">Optional name of collection inside the objects to walk for example childNodes.</param>
	/// <param name="s" type="String">Optional scope to execute the function in.</param>
}

tinymce.createNS = function(n, o) {
	/// <summary>Creates a namespace on a specific object.</summary>
	/// <param name="n" type="String">Namespace to create for example a.b.c.d.</param>
	/// <param name="o" type="Object">Optional object to add namespace to, defaults to window.</param>
	/// <returns type="Object">New namespace object the last item in path.</returns>
}

tinymce.resolve = function(n, o) {
	/// <summary>Resolves a string and returns the object from a specific structure.</summary>
	/// <param name="n" type="String">Path to resolve for example a.b.c.d.</param>
	/// <param name="o" type="Object">Optional object to search though, defaults to window.</param>
	/// <returns type="Object">Last object in path or null if it couldn't be resolved.</returns>
}

tinymce.addUnload = function(f, s) {
	/// <summary>Adds an unload handler to the document.</summary>
	/// <param name="f" type="function">Function to execute before the document gets unloaded.</param>
	/// <param name="s" type="Object">Optional scope to execute the function in.</param>
	/// <returns type="function">Returns the specified unload handler function.</returns>
}

tinymce.removeUnload = function(f) {
	/// <summary>Removes the specified function form the unload handler list.</summary>
	/// <param name="f" type="function">Function to remove from unload handler list.</param>
	/// <returns type="function">Removed function name or null if it wasn't found.</returns>
}

tinymce.explode = function(s, d) {
	/// <summary>Splits a string but removes the whitespace before and after each value.</summary>
	/// <param name="s" type="string">String to split.</param>
	/// <param name="d" type="string">Delimiter to split by.</param>
}

tinyMCE = tinymce;
