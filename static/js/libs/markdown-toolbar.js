/* global define, jQuery, commonmark, emoji */
/* global require, module */

(function(factory) {
    if (typeof define === 'function' && define.amd) {
        define(['jquery', 'commonmark'], factory);
    } else if (typeof exports === 'object') {
        factory(require('jquery'), require('commonmark'));
    } else {
        factory(jQuery, commonmark);
    }
}(function($, commonmark) {
    var MarkdownRenderer = function() {
        this.reader = new commonmark.Parser();
        this.writer = new commonmark.HtmlRenderer();
        if (typeof emoji !== 'undefined') {
            if (window.STATIC_URL) {
                emoji.sheet_path = window.STATIC_URL +
                    'emoji-data/sheet_apple_64.png';
            }
            emoji.use_sheet = true;
            // Temporary workaround for img_path issue:
            // https://github.com/iamcal/js-emoji/issues/47
            emoji.img_sets[emoji.img_set].sheet = emoji.sheet_path;
        }
    };

    /**
     * MarkdownRenderer.render does a few things to its input text:
     * - Renders the text with CommonMark
     * - Transforms emojis
     * - Turns URLs into <a> tags
     */
    MarkdownRenderer.prototype.render = function(text) {
        var parsed = this.reader.parse(text);
        var rendered = this.writer.render(parsed);
        if (typeof window !== 'undefined' &&
            typeof window.linkifyHtml === 'function'
        ) {
            rendered = window.linkifyHtml(rendered);
        }
        if (typeof emoji !== 'undefined' &&
            typeof emoji.replace_colons === 'function'
        ) {
            rendered = emoji.replace_colons(rendered);
        }
        return rendered;
    };

    var MarkdownPreview = function($textarea, $previewArea) {
        this.renderer = new MarkdownRenderer();
        this.$textarea = $textarea;
        this.$previewArea = $previewArea;
        this._startEventHandler();
    };

    /**
     * Refresh the markdown preview, given the source text.
     */
    MarkdownPreview.prototype.refresh = function(text) {
        var rendered = this.renderer.render(text);
        this.$previewArea.html(rendered);
    };

    MarkdownPreview.prototype._startEventHandler = function() {
        var me = this;
        this.$textarea.on('change keyup', function(e) {
            var comment = $(e.target).val();
            me.refresh(comment);
        });
    };

    var MarkdownToolbarController = function() {
        this.prefixLength = null;
        this.selectionStart = null;
        this.selectionEnd = null;
    };

    /**
     * Given a multiline text string, replace the newlines with
     * ascending numbers to make an ordered list.
     */
    MarkdownToolbarController.prototype.makeOrderedList = function(text) {
        var lines = text.split(/\r?\n|↵/);
        var i;
        for (i = 0; i < lines.length; i++) {
            lines[i] = (i + 1) + '. ' + lines[i];
            if (i > 0) {
                lines[i] = '\n' + lines[i];
            }
        }
        return lines.join('');
    };

    MarkdownToolbarController.prototype.render = function(
        d, selectionStart, selectionEnd, text
    ) {
        var selectedText = text.substr(selectionStart, selectionEnd - selectionStart);
        if (d.prefix === '# ' && selectionStart !== 0 && text.substr(selectionStart -2, 1) === '#') {
            d.prefix = '#';
            selectionStart -= 2;
        }
        var suffixdiff = 0;
        var prefixdiff = 0;
        if (selectedText.match(/\n/) &&
            d.blockPrefix &&
            d.blockSuffix
        ) {
            if (d.blockPrefix) {
                text = this.renderBlockPrefix(
                    selectionStart, selectionEnd, d, text);
                prefixdiff += d.blockPrefix.length + 1;
            }

            if (d.blockSuffix) {
                text = this.renderBlockSuffix(
                    selectionStart, selectionEnd, d.blockPrefix.length,
                    d, text);
                suffixdiff += d.blockSuffix.length + 1;
            }
        } else {
            if (d.prefix) {
                text = this.renderPrefix(
                    selectionStart, selectionEnd, d, text);
                prefixdiff += d.prefix.length;
            }

            if (d.suffix) {
                text = this.renderSuffix(
                    selectionStart, selectionEnd, this.prefixLength,
                    d, text);
                suffixdiff += d.suffix.length;
            }
        }

        if (d.prefix === '#' && text.substr(selectionStart, 1) === '#') {
            selectionStart += 2;
        }

        if (d.prefix === '![](url)') {
            this.selectionStart = selectionEnd + 4;
            this.selectionEnd = selectionEnd + 7;
        } else if (d.multiline && selectedText.match(/\n/)) {
            this.selectionStart = selectionStart;
            this.selectionEnd = selectionEnd + (prefixdiff + suffixdiff) * (selectedText.match(/\n/g).length + 1);
        } else {
            this.selectionStart = selectionStart + prefixdiff;
            this.selectionEnd = selectionEnd + prefixdiff;
        }

        return text;
    };

    MarkdownToolbarController.prototype.renderPrefix = function(
        selectionStart, selectionEnd, d, text
    ) {
        this.prefixLength = d.prefix.length;
        var s;

        if (d.multiline) {
            var before = text.substr(0, selectionStart);
            var snippet = text.substr(selectionStart, selectionEnd - selectionStart);
            var after = text.substr(selectionEnd, text.length - selectionEnd);
            if (d.prefix === '1. ') {
                // Create the numbered list
                snippet = this.makeOrderedList(snippet);
            } else {
                snippet = snippet.replace(/^/, d.prefix);
                snippet = snippet.replace(/\n/g, '\n' + d.prefix);
            }
            s = before + snippet + after;
        } else {
            s = text.substr(0, selectionStart);
            s += d.prefix;
            s += text.substr(selectionStart, text.length - selectionStart);
        }
        return s;
    };

    MarkdownToolbarController.prototype.renderSuffix = function(
        selectionStart, selectionEnd, prefixLength, d, text
    ) {
        selectionEnd += prefixLength;
        var s = text.substr(0, selectionEnd);
        s += d.suffix;
        s += text.substr(selectionEnd, text.length - selectionEnd);
        return s;
    };

    MarkdownToolbarController.prototype.renderBlockPrefix = function(
        selectionStart, selectionEnd, d, text
    ) {
        this.prefixLength = d.blockPrefix.length + 1;
        var s = text.substr(0, selectionStart);
        s += d.blockPrefix + '\n';
        s += text.substr(selectionStart, text.length - selectionStart);
        return s;
    };

    MarkdownToolbarController.prototype.renderBlockSuffix = function(
        selectionStart, selectionEnd, blockPrefixLength, d, text
    ) {
        selectionEnd += blockPrefixLength + 1;
        var s = text.substr(0, selectionEnd);
        s += '\n' + d.blockSuffix;
        s += text.substr(selectionEnd, text.length - selectionEnd);
        return s;
    };

    var MarkdownToolbar = function($toolbar, $textarea, markdownPreview) {
        this.$toolbar = $toolbar;
        this.$textarea = $textarea;
        this.markdownPreview = markdownPreview;
        this.lastHotkey = null;
        this.lastText = null;
        this.init();
    };

    MarkdownToolbar.prototype.init = function() {
        var me = this;

        this.$toolbar.find('button.js-toolbar-item').on('click', function() {
            var $this = $(this);

            // Get data from button element
            var buttonData = $this.data();

            // Get cursor position and textarea's text
            var selectionStart = me.$textarea[0].selectionStart;
            var selectionEnd = me.$textarea[0].selectionEnd;
            var text = me.$textarea.val();
            
            if (buttonData.hotkey === 'p') {
                if (me.markdownPreview) {
                    me.markdownPreview.refresh(me.$textarea.val());
                    if (me.markdownPreview.$previewArea.attr('auto_preview') === true) {
                        me.markdownPreview.$previewArea.show();
                        me.markdownPreview.$previewArea.attr('auto_preview', false);
                    } else {
                        me.markdownPreview.$previewArea.toggle();
                    }
                    me.markdownPreview.$previewArea.width(me.$textarea.outerWidth());
                }
                return;
            } else if (buttonData.hotkey === me.lastHotkey && buttonData.hotkey !== 'h' && me.lastText) {
                var diff = text.length - me.lastText.length;
                if (buttonData.multiline) {
                    selectionEnd -= diff;
                } else {
                    selectionStart -= diff / 2;
                    selectionEnd -= diff / 2;
                }
                text = me.lastText;
                me.lastHotkey = null;
            } else {
                var mtc = new MarkdownToolbarController();
                me.lastText = text;
                text = mtc.render(
                    buttonData, selectionStart, selectionEnd, text);
                selectionStart = mtc.selectionStart;
                selectionEnd = mtc.selectionEnd;
                me.lastHotkey = buttonData.hotkey;
            }

            me.$textarea.val(text);

            // Reset cursor to original state
            me.$textarea.focus();
            me.$textarea[0].setSelectionRange(selectionStart, selectionEnd);
            
            // Refresh the preview view if it exists.
            if (me.markdownPreview &&
                typeof me.markdownPreview.refresh === 'function'
            ) {
                me.markdownPreview.refresh(me.$textarea.val());
                me.markdownPreview.$previewArea.width(me.$textarea.outerWidth());
            }
        });

        this.$textarea.on('keyup', function() {
            me.lastHotkey = null;
        });

        // Handle a resize of the textarea - 'resize' event doesn't work
        // store init (default) state   
        this.$textarea.data('x', this.$textarea.outerWidth());
        this.$textarea.data('y', this.$textarea.outerHeight()); 

        this.$textarea.mouseup(function(){
            var $this = jQuery(this);

            if (  $this.outerWidth()  != $this.data('x') 
                || $this.outerHeight() != $this.data('y') )
            {
                // Resize Action Here
                me.markdownPreview.$previewArea.width(me.$textarea.outerWidth());
            }

            // store new height/width
            $this.data('x', $this.outerWidth());
            $this.data('y', $this.outerHeight()); 
        });
    };

    var toolbarMarkup = '<div class="markdown-toolbar">' +
    '<div class="toolbar-group">' +
        '<div class="toolbar-item dropdown js-menu-container">' +
        '</div>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Add header text"' +
                'tabindex="-1"' +
                'data-prefix="# "' +
                'data-hotkey="h"' +
                'data-ga-click="Markdown Toolbar, click, heading"' +
                'data-surround-with-newlines="true">' +
            '<svg class="octicon octicon-text-size" viewBox="0 0 18 16" version="1.1" width="18" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M13.62 9.08L12.1 3.66h-.06l-1.5 5.42h3.08zM5.7 10.13S4.68 6.52 4.53 6.02h-.08l-1.13 4.11H5.7zM17.31 14h-2.25l-.95-3.25h-4.07L9.09 14H6.84l-.69-2.33H2.87L2.17 14H0l3.3-9.59h2.5l2.17 6.34L10.86 2h2.52l3.94 12h-.01z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Add bold text"' +
                'tabindex="-1"' +
                'data-prefix="**"' +
                'data-suffix="**"' +
                'data-hotkey="b"' +
                'data-ga-click="Markdown Toolbar, click, bold">' +
            '<svg aria-hidden="true" class="octicon octicon-bold" height="16" role="img" version="1.1" viewBox="0 0 10 16" width="10"><path d="M0 2h3.83c2.48 0 4.3 0.75 4.3 2.95 0 1.14-0.63 2.23-1.67 2.61v0.06c1.33 0.3 2.3 1.23 2.3 2.86 0 2.39-1.97 3.52-4.61 3.52H0V2z m3.66 4.95c1.67 0 2.38-0.66 2.38-1.69 0-1.17-0.78-1.61-2.34-1.61H2.13v3.3h1.53z m0.27 5.39c1.77 0 2.75-0.64 2.75-1.98 0-1.27-0.95-1.81-2.75-1.81H2.13v3.8h1.8z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Add italic text"' +
                'tabindex="-1"' +
                'data-prefix="_"' +
                'data-suffix="_"' +
                'data-hotkey="i"' +
                'data-ga-click="Markdown Toolbar, click, italic">' +
            '<svg aria-hidden="true" class="octicon octicon-italic" height="16" role="img" version="1.1" viewBox="0 0 6 16" width="6"><path d="M2.81 5h1.98L3 14H1l1.81-9z m0.36-2.7c0-0.7 0.58-1.3 1.33-1.3 0.56 0 1.13 0.38 1.13 1.03 0 0.75-0.59 1.3-1.33 1.3-0.58 0-1.13-0.38-1.13-1.03z"></path></svg>' +
        '</button>' +
    '</div>' +
    '<div class="toolbar-group">' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Insert a quote"' +
                'tabindex="-1"' +
                'data-prefix="> "' +
                'data-multiline="true"' +
                'data-ga-click="Markdown Toolbar, click, quote"' +
                'data-surround-with-newlines="true">' +
            '<svg aria-hidden="true" class="octicon octicon-quote" height="16" role="img" version="1.1" viewBox="0 0 14 16" width="14"><path d="M6.16 3.17C3.73 4.73 2.55 6.34 2.55 9.03c0.16-0.05 0.3-0.05 0.44-0.05 1.27 0 2.5 0.86 2.5 2.41 0 1.61-1.03 2.61-2.5 2.61C1.09 14 0 12.48 0 9.75 0 5.95 1.75 3.22 5.02 1.33l1.14 1.84z m7 0C10.73 4.73 9.55 6.34 9.55 9.03c0.16-0.05 0.3-0.05 0.44-0.05 1.27 0 2.5 0.86 2.5 2.41 0 1.61-1.03 2.61-2.5 2.61-1.89 0-2.98-1.52-2.98-4.25 0-3.8 1.75-6.53 5.02-8.42l1.14 1.84z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Insert code" tabindex="-1"' +
                'data-prefix="`"' +
                'data-suffix="`"' +
                'data-block-prefix="```"' +
                'data-block-suffix="```"' +
                'data-ga-click="Markdown Toolbar, click, code">' +
            '<svg aria-hidden="true" class="octicon octicon-code" height="16" role="img" version="1.1" viewBox="0 0 14 16" width="14"><path d="M9.5 3l-1.5 1.5 3.5 3.5L8 11.5l1.5 1.5 4.5-5L9.5 3zM4.5 3L0 8l4.5 5 1.5-1.5L2.5 8l3.5-3.5L4.5 3z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Add a bulleted list"' +
                'tabindex="-1"' +
                'data-multiline="true"' +
                'data-prefix="- "' +
                'data-ga-click="Markdown Toolbar, click, unordered list"' +
                'data-surround-with-newlines="true">' +
            '<svg aria-hidden="true" class="octicon octicon-list-unordered" height="16" role="img" version="1.1" viewBox="0 0 12 16" width="12"><path d="M2 13c0 0.59 0 1-0.59 1H0.59c-0.59 0-0.59-0.41-0.59-1s0-1 0.59-1h0.81c0.59 0 0.59 0.41 0.59 1z m2.59-9h6.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1H4.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1zM1.41 7H0.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1h0.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1z m0-5H0.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1h0.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1z m10 5H4.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1h6.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1z m0 5H4.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1h6.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Add a numbered list"' +
                'tabindex="-1"' +
                'data-prefix="1. "' +
                'data-multiline="true"' +
                'data-ga-click="Markdown Toolbar, click, ordered list"' +
                'data-ordered-list="true">' +
            '<svg aria-hidden="true" class="octicon octicon-list-ordered" height="16" role="img" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 13c0 0.59 0 1-0.59 1H4.59c-0.59 0-0.59-0.41-0.59-1s0-1 0.59-1h6.81c0.59 0 0.59 0.41 0.59 1zM4.59 4h6.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1H4.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1z m6.81 3H4.59c-0.59 0-0.59 0.41-0.59 1s0 1 0.59 1h6.81c0.59 0 0.59-0.41 0.59-1s0-1-0.59-1zM2 1H1.28C0.98 1.19 0.7 1.25 0.25 1.34v0.66h0.75v2.14H0.16v0.86h2.84v-0.86h-1V1z m0.25 8.13c-0.17 0-0.45 0.03-0.66 0.06 0.53-0.56 1.14-1.25 1.14-1.89-0.02-0.78-0.56-1.3-1.36-1.3-0.59 0-0.97 0.2-1.38 0.64l0.58 0.58c0.19-0.19 0.38-0.38 0.64-0.38 0.28 0 0.48 0.16 0.48 0.52 0 0.53-0.77 1.2-1.7 2.06v0.58h3l-0.09-0.88h-0.66z m-0.08 3.78v-0.03c0.44-0.19 0.64-0.47 0.64-0.86 0-0.7-0.56-1.11-1.44-1.11-0.48 0-0.89 0.19-1.28 0.52l0.55 0.64c0.25-0.2 0.44-0.31 0.69-0.31 0.27 0 0.42 0.13 0.42 0.36 0 0.27-0.2 0.44-0.86 0.44v0.75c0.83 0 0.98 0.17 0.98 0.47 0 0.25-0.23 0.38-0.58 0.38-0.28 0-0.56-0.14-0.81-0.38L0 14.44c0.3 0.36 0.77 0.56 1.41 0.56 0.83 0 1.53-0.41 1.53-1.16 0-0.5-0.31-0.81-0.77-0.94z"></path></svg>' +
        '</button>' +
    '</div>' +
    '<div class="toolbar-group">' +
        '<button type="button"' +
            'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
            'title="Add a link" tabindex="-1"' +
            'data-prefix="["' +
            'data-suffix="](url)"' +
            'data-replace-next="url"' +
            'data-hotkey="k"' +
            'data-scan-for="https?://"' +
            'data-ga-click="Markdown Toolbar, click, link">' +
        '<svg aria-hidden="true" class="octicon octicon-link" height="16" role="img" version="1.1" viewBox="0 0 16 16" width="16"><path d="M4 9h1v1h-1c-1.5 0-3-1.69-3-3.5s1.55-3.5 3-3.5h4c1.45 0 3 1.69 3 3.5 0 1.41-0.91 2.72-2 3.25v-1.16c0.58-0.45 1-1.27 1-2.09 0-1.28-1.02-2.5-2-2.5H4c-0.98 0-2 1.22-2 2.5s1 2.5 2 2.5z m9-3h-1v1h1c1 0 2 1.22 2 2.5s-1.02 2.5-2 2.5H9c-0.98 0-2-1.22-2-2.5 0-0.83 0.42-1.64 1-2.09v-1.16c-1.09 0.53-2 1.84-2 3.25 0 1.81 1.55 3.5 3 3.5h4c1.45 0 3-1.69 3-3.5s-1.5-3.5-3-3.5z"></path></svg>' +
        '</button>' +
        '<button type="button"' +
            'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
            'title="Add an image" tabindex="-1"' +
            'data-prefix="![](url)"' +
            'data-replace-next="url"' +
            'data-hotkey="f"' +
            'data-ga-click="Markdown Toolbar, click, image">' +
        '<svg aria-hidden="true" class="octicon octicon-file-media"  height="16" version="1.1" viewBox="0 0 16 16" width="16"><path fill-rule="evenodd" d="M6 5h2v2H6V5zm6-.5V14c0 .55-.45 1-1 1H1c-.55 0-1-.45-1-1V2c0-.55.45-1 1-1h7.5L12 4.5zM11 5L8 2H1v11l3-5 2 4 2-2 3 3V5z"></path></svg>' +
        '</button>' +
    '</div>' +
    '<div class="toolbar-group">' +
        '<button type="button"' +
                'class="js-toolbar-item toolbar-item tooltipped tooltipped-n"' +
                'title="Toggle Preview"' +
                'tabindex="-1"' +
                'data-hotkey="p"' +
                'data-ga-click="Markdown Toolbar, click, toggle preview"' +
                '>' +
            '<svg class="octicon octicon-eye" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M8.06 2C3 2 0 8 0 8s3 6 8.06 6C13 14 16 8 16 8s-3-6-7.94-6zM8 12c-2.2 0-4-1.78-4-4 0-2.2 1.8-4 4-4 2.22 0 4 1.8 4 4 0 2.22-1.78 4-4 4zm2-4c0 1.11-.89 2-2 2-1.11 0-2-.89-2-2 0-1.11.89-2 2-2 1.11 0 2 .89 2 2z"></path></svg>' +
        '</button>' +
    '</div>' +
        '</div>';
    if (typeof $.fn !== 'undefined') {
        $.fn.markdownToolbar = function(auto_preview) {
            var $this = $(this);
            var $toolbar = $(toolbarMarkup);
            $this.before($toolbar);
            var $preview = $('<div class="markdown-preview"></div>');
            if (auto_preview === false) {
                $preview.hide();
            } else {
                auto_preview = true;
            }
            $preview.attr('auto_preview', auto_preview);
            $this.after($preview);
            var markdownPreview = undefined;
            markdownPreview = new MarkdownPreview($this, $preview);

            new MarkdownToolbar($toolbar, $this, markdownPreview);
        };

        $.fn.markdownToolbar.version = '1.0.0';
    }

    if (typeof module !== 'undefined') {
        module.exports = {
            MarkdownRenderer: MarkdownRenderer,
            MarkdownToolbarController: MarkdownToolbarController
        };
    }
}));
