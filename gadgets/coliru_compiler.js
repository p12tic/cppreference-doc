/*
    Copyright (C) 2013  Povilas Kanapickas <povilas@radix.lt>

    This file is part of cppreference.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
*/

String.prototype.trim = function () {
    return this.replace(/^\s+|\s+$/g, "");
};

/* We add two new divs for the live editor and the program output. The divs are
   inserted after the geshi code and output respectively. This way the ACE
   editor and the compilation output are independent from the static geshi
   text. We can easily switch between the live editor and the static version.
*/
function Editor(root) {

    var cmd_info_cxx = {
        cc: [
            { title: 'GCC 4.6', cmd: 'g++-4.6 -std=c++98 ' },
            { title: 'GCC 4.7', cmd: 'g++-4.7 -std=c++98 ' },
            { title: 'GCC 4.7 (C++11)', cmd: 'g++-4.7 -std=c++11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 4.8', cmd: 'g++-4.8 -std=c++98 ' },
            { title: 'GCC 4.8 (C++11)', cmd: 'g++-4.8 -std=c++11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 4.9', cmd: 'g++-4.9 -std=c++98 ' },
            { title: 'GCC 4.9 (C++11)', cmd: 'g++-4.9 -std=c++11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 4.9 (C++14)', cmd: 'g++-4.9 -std=c++14 ', opt_suff: ' -latomic ' },
            { title: 'GCC 5.2 (C++98)', cmd: 'g++-5.2 -std=c++98 ' },
            { title: 'GCC 5.2 (C++11)', cmd: 'g++-5.2 -std=c++11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 5.2 (C++14)', cmd: 'g++-5.2 -std=c++14 ', opt_suff: ' -latomic ' },
            { title: 'GCC 5.2 (C++17)', cmd: 'g++-5.2 -std=c++1z ', opt_suff: ' -latomic ' },
            { title: 'GCC 6.1 (C++98)', cmd: 'g++ -std=c++98 ' },
            { title: 'GCC 6.1 (C++11)', cmd: 'g++ -std=c++11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 6.1 (C++14)', cmd: 'g++ -std=c++14 ', opt_suff: ' -latomic ' },
            { title: 'GCC 6.1 (C++17)', cmd: 'g++ -std=c++1z ', opt_suff: ' -latomic ' },
            { title: 'GCC 6.1 (C++17 + Concepts TS + TM TS + Filesystem TS)',
                cmd: 'g++ -std=c++1z -fconcepts -fgnu-tm ',
                opt_suff: ' -latomic -lstdc++fs ' },
            { title: 'clang 3.8', cmd: 'clang++ -std=c++98 ' },
            { title: 'clang 3.8 (C++11)',
              cmd: 'clang++ -std=c++11 -stdlib=libc++ ',
              opt_suff: ' -latomic -lsupc++ '
            },
            { title: 'clang 3.8 (C++14)',
              cmd: 'clang++ -std=c++14 -stdlib=libc++ ',
              opt_suff: ' -latomic -lsupc++ '
            },
            { title: 'clang 3.8 (C++17)',
              cmd: 'clang++ -std=c++1z -stdlib=libc++ ',
              opt_suff: ' -latomic -lsupc++ '
            }
        ],
        default_id: 16,
        opt: ' -O2 -Wall -Wextra -pedantic -pthread -pedantic-errors main.cpp -lm ',
    }

    var cmd_info_c = {
        cc: [
            { title: 'GCC 4.6', cmd: 'gcc-4.6 -x c -std=c89 ' },
            { title: 'GCC 4.7', cmd: 'gcc-4.7 -x c -std=c89 ' },
            { title: 'GCC 4.8', cmd: 'gcc-4.8 -x c -std=c89 ' },
            { title: 'GCC 4.8 (C99)', cmd: 'g++-4.8 -x c -std=c99 ' },
            { title: 'GCC 4.9', cmd: 'gcc-4.9 -x c -std=c89 ' },
            { title: 'GCC 4.9 (C99)', cmd: 'g++-4.9 -x c -std=c99 ' },
            { title: 'GCC 4.9 (C11)', cmd: 'g++-4.9 -x c -std=c11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 5.2 (C89)', cmd: 'g++-5.2 -x c -std=c89 ' },
            { title: 'GCC 5.2 (C99)', cmd: 'g++-5.2 -x c -std=c99 ' },
            { title: 'GCC 5.2 (C11)', cmd: 'g++-5.2 -x c -std=c11 ', opt_suff: ' -latomic ' },
            { title: 'GCC 6.1 (C89)', cmd: 'g++ -x c -std=c89 ' },
            { title: 'GCC 6.1 (C99)', cmd: 'g++ -x c -std=c99 ' },
            { title: 'GCC 6.1 (C11)', cmd: 'g++ -x c -std=c11 ', opt_suff: ' -latomic ' },
            { title: 'clang 3.8', cmd: 'clang -x c -std=c89 -Wno-newline-eof ' },
            { title: 'clang 3.8 (C99)', cmd: 'clang++ -x c -std=c99 -Wno-newline-eof '},
            { title: 'clang 3.8 (C11)', cmd: 'clang++ -x c -std=c11 -Wno-newline-eof ', opt_suff: ' -latomic '}
        ],
        default_id: 12,
        opt: ' -O2 -Wall -Wextra -pedantic -pthread -pedantic-errors main.cpp -lm ',
    }

    var std_ids = {
        'cxx98' : { c: 'cxx', id: 5 },
        'cxx03' : { c: 'cxx', id: 5 },
        'cxx11' : { c: 'cxx', id: 6 },
        'cxx14' : { c: 'cxx', id: 7 },
        'c89' : { c: 'cc', id: 4 },
        'c99' : { c: 'cc', id: 5 },
        'c11' : { c: 'cc', id: 6 }
    }

    this.get_std_id = function() {
        if (this.root.hasClass('t-example-std-cxx98'))
            return 'cxx98'
        if (this.root.hasClass('t-example-std-cxx03'))
            return 'cxx03'
        if (this.root.hasClass('t-example-std-cxx11'))
            return 'cxx11'
        if (this.root.hasClass('t-example-std-cxx14'))
            return 'cxx14'
        if (this.root.hasClass('t-example-std-c89'))
            return 'c89'
        if (this.root.hasClass('t-example-std-c99'))
            return 'c99'
        if (this.root.hasClass('t-example-std-c11'))
            return 'c11'
        return null;
    }

    this.std_id = this.get_std_id();

    this.check_is_cxx = function() {
        if (this.std_id == null) {
            if (mw.config.get('wgTitle').indexOf('c/') == 0) {
                return false;
            } else {
                return true;
            }
        }

        if (this.std_ids[this.std_id].c == 'cc')
            return false
        return true
    };

    if (this.check_is_cxx()) {
        this.cmd_info = cmd_info_cxx;
    } else {
        this.cmd_info = cmd_info_c;
    }

    this.get_cmd_default_id = function() {
        if (this.std_id == null) {
            return this.cmd_info.default_id;
        } else {
            return this.cmd_ids[this.cmd_id].id;
        }
    }

    this.cmd_default_id = this.get_cmd_default_id();

    this.cmd_run_normal = ' 2>&1 | sed "s/^/☘/"; if [ -x a.out ]; then ./a.out | sed "s/^/☢/"; fi'
    this.cmd_run_share = ' && ./a.out';

    this.el = {};
    this.el.root = root;
    this.is_orig = true;

    this.el.action_bar = this.el.root.children('.t-example-live-link:first');

    // initialize the action bar
    this.el.run_init_btn = this.el.action_bar.children('.coliru-btn-run-init');
    this.el.run_btn = $('<div>Run</div>')
                        .addClass('coliru-btn coliru-btn-run')
                        .hide().appendTo(this.el.action_bar);
    this.el.share_btn = $('<div>Share</div>')
                        .addClass('coliru-btn coliru-btn-share')
                        .hide().appendTo(this.el.action_bar);
    this.el.exit_btn = $('<div>Exit</div>')
                        .addClass('coliru-btn coliru-btn-exit')
                        .hide().appendTo(this.el.action_bar);

    this.el.cc_select_div = $('<div/>')
                        .addClass('coliru-select-compiler')
                        .hide().appendTo(this.el.action_bar);
    this.el.cc_select = $('<select/>').appendTo(this.el.cc_select_div);

    for (var i = 0; i < this.cmd_info.cc.length; ++i) {
        var cmd = this.cmd_info.cc[i];
        $('<option/>').text(cmd.title).attr('value', i.toString())
                                      .appendTo(this.el.cc_select);
    }
    this.el.cc_select.val(this.cmd_default_id.toString());

    this.el.pwr = $('<div>Powered by <a href="http://coliru.stacked-crooked.com">Coliru</a> online compiler</div>')
                        .addClass('coliru-powered')
                        .hide().appendTo(this.el.action_bar);

    // find and store the original code and output divs
    orig_code = this.el.root.children('.mw-geshi:first');
    if (orig_code.length > 0) {
        this.has_orig_code = true;
        this.el.orig_code = orig_code.first();
    } else {
        this.has_orig_code = false;
        this.el.orig_code = $('<div/>').hide().insertAfter(this.el.action_bar);
    }

    orig_output = this.el.root.children('.mw-geshi:last');
    if (orig_output.length > 0 && !orig_output.is(orig_code)) {
        this.has_orig_output = true;
        this.el.orig_output = orig_output.first();
    } else {
        this.has_orig_output = false;
        this.el.output_p = $('<p>Output:</p>').hide().insertAfter(this.el.orig_code);
        this.el.orig_output = $('<div/>').hide().insertAfter(this.el.output_p);
    }

    if (this.has_orig_code) {
        this.source_code = this.el.orig_code.text().replace(/\u00a0/g, " ");
    } else {
        this.source_code = '';
    }

    // initialize the editor
    this.el.edited_code = $('<div/>').addClass('t-example-code mw-geshi')
                                     .hide().insertAfter(this.el.orig_code);
    this.el.editor_div = $('<div/>').addClass('ace_editor ace-tm')
                                    .appendTo(this.el.edited_code);
    this.editor = ace.edit(this.el.editor_div.get(0));
    this.editor.setTheme("ace/theme/textmate");
    this.editor.getSession().setMode("ace/mode/c_cpp");

    this.editor.commands.bindKeys({"Ctrl-l":null});
    this.editor.commands.bindKeys({"Ctrl-t":null});
    this.editor.commands.bindKeys({"Command-l":null});
    this.editor.commands.addCommand({
        name: 'Build and run',
        bindKey: {win: 'Ctrl-B', mac: 'Command-B'},
        exec: function(editor) { this.compile_now(); },
        readOnly: true
    });
    this.editor.commands.addCommand({
        name: 'Disable Ctrl-S',
        bindKey: {win: 'Ctrl-S', mac: 'Command-S'},
        exec: function(editor) {},
        readOnly: true
    });

    this.editor.getSession().setValue(this.source_code);

    // create compiler output block
    this.el.compiler_output_p = $('<p>Compiler messages:</p>')
                                  .hide().insertAfter(this.el.edited_code);
    this.el.compiler_output = $('<div/>').addClass('coliru-output coliru-output-compiler mw-geshi')
                                         .hide().insertAfter(this.el.compiler_output_p);
    this.el.compiler_output_div = $('<div/>').appendTo(this.el.compiler_output);

    // create output block
    this.el.edited_output = $('<div/>').addClass('coliru-output coliru-output-program mw-geshi')
                                       .hide().insertAfter(this.el.orig_output);
    this.el.output_div = $('<div/>').appendTo(this.el.edited_output);

    this.reset_editor = function() {
        this.editor.getSession().setValue(this.source_code);
    };

    this.el.run_btn.click(function() {
        if (!this.el.run_btn.hasClass('coliru-btn-disabled')) {
            this.compile_now();
        }
    }.bind(this));
    this.el.share_btn.click(function() {
        if (!this.el.share_btn.hasClass('coliru-btn-disabled')) {
            this.share();
        }
    }.bind(this));
    this.el.exit_btn.click(function() {
        if (!this.el.exit_btn.hasClass('coliru-btn-disabled')) {
            this.restore_orig();
        }
    }.bind(this));

    this.enable_ui = function(value) {
        this.editor.setReadOnly(!value);

        if (value) {
            this.el.run_btn.removeClass('coliru-btn-disabled');
            this.el.share_btn.removeClass('coliru-btn-disabled');
            this.el.exit_btn.removeClass('coliru-btn-disabled');
        } else {
            this.el.run_btn.addClass('coliru-btn-disabled');
            this.el.share_btn.addClass('coliru-btn-disabled');
            this.el.exit_btn.addClass('coliru-btn-disabled');
        }
    };

    this.send = function(location, cmd, src, f) {
        this.enable_ui(false);

        var http_request = new XMLHttpRequest();
        http_request.open("POST",
                          "http://coliru.stacked-crooked.com/" + location, true);
        var parent = this;
        http_request.onreadystatechange = function() {
            if (http_request.readyState == 4) {
                parent.enable_ui(true);
                if (http_request.status == 200) {
                    parent.last_result = http_request.responseText.trim();
                    f({src: parent.editor.getValue(),
                       cmd: parent.cmd,
                       output: parent.last_result});
                }
            }
        };
        var post_data = JSON.stringify({
            "cmd" : cmd, "src" : src
        });
        http_request.send(post_data);
    };

    this.compile_now = function() {
        var parent = this;
        this.editor.getSession().clearAnnotations();
        this.el.compiler_output_p.fadeOut('fast');
        this.el.compiler_output.fadeOut('fast');

        this.el.output_div.html('Building and running...');

        var cmd = this.get_cmd(false);
        var src = this.editor.getValue();

        this.send("compile", cmd, src, function(obj) {
            var lines = obj.output.split(/\n/);

            // analyze the compiler output
            var annotations = [];
            var annotation_lines = [];

            var program_output = '';
            var compiler_output = '';

            for (var i = 0; i !== lines.length; ++i) {
                var line = lines[i];

                var is_compile_output = false;
                var is_shell_output = false;

                if (line.indexOf('☘') == 0) {
                    is_compile_output = true;
                    line = line.substring(1);
                } else if (line.indexOf('☢') == 0) {
                    line = line.substring(1);
                } else {
                    // everything else comes from the shell. Presumably, this
                    // indicates a serious error in the program
                    // (e.g. it segfaults).
                    // FIXME: probably need a better API
                    is_shell_output = true;
                }

                if (line !== '') {

                    line = line.replace(/</g, '&lt').replace(/>/g, '&gt');

                    if (is_compile_output) {
                        // check if line contains an error
                        var has_error = false, has_any_error = false;
                        var error_lineno = 0;
                        var error_text = "";

                        var match = line.match(/^main.cpp:(\d+):\d+:(.*)/);
                        if (match) {
                            has_error = true;
                            error_lineno = parseInt(match[1]);
                            error_text = match[2].trim();
                        }

                        // add annotation if possible
                        if (has_error) {
                            if (annotation_lines.indexOf(error_lineno) === -1) {
                                var error_type = 'error';
                                if (error_text.match(/^warning:/)) {
                                    error_type = 'warning';
                                }

                                annotation_lines.push(error_lineno);
                                annotations.push({row: error_lineno-1, column: 0,
                                                text: error_text, type:error_type});
                            }
                        }

                        // highlight the output line if possible
                        pre_open = '<pre';
                        if (has_error) {
                            pre_open += ' onclick="window.jump_to_error(this, '
                                    + error_lineno + ')" onmouseover="window.highlight_error(this, true)" onmouseout="window.highlight_error(this, false)"';
                        }
                        pre_open += '>';
                        pre_close = '</pre>';
                        compiler_output += pre_open + line + pre_close;
                    } else if (is_shell_output) {
                        pre_open = '<pre class="coliru-output-line-shell">';
                        pre_close = '</pre>';
                        program_output += pre_open + line + pre_close;
                    } else {
                        pre_open = '<pre class="coliru-output-line-exe">';
                        pre_close = '</pre>';
                        program_output += pre_open + line + pre_close;
                    }
                } else {
                    program_output += '<br/>';
                }
            }

            parent.el.output_div.html(program_output);

            if (compiler_output !== '') {
                parent.el.compiler_output_div.html(compiler_output);
                parent.el.compiler_output_p.fadeIn('fast');
                parent.el.compiler_output.fadeIn('fast');
            }

            // mark the errors in the code
            window.setTimeout(function() {
                parent.editor.getSession().setAnnotations(annotations);
            }, 100);
        });
    };

    this.share = function() {
        var cmd = this.get_cmd(true);
        var src = this.editor.getValue();

        this.send("share", cmd, src, function (obj) {
            var url = "http://coliru.stacked-crooked.com/view?id=" + obj.output;
            window.open(url, '_blank');
        })
    };

    this.get_cmd = function(is_shared) {
        var val = this.el.cc_select.val();
        var cc = this.cmd_info.cc[parseInt(val)].cmd;
        cc = cc + this.cmd_info.opt
        if (this.cmd_info.cc[parseInt(val)].opt_suff !== undefined) {
            cc = cc + this.cmd_info.cc[parseInt(val)].opt_suff;
        }
        if (is_shared) {
            return cc + this.cmd_run_share;
        } else {
            return cc + this.cmd_run_normal;
        }
    };

    this.replace_orig = function() {
        if (!this.is_orig) {
            return; // already replaced
        }

        this.el.root.height(this.el.root.height());

        var parent = this;
        this.el.run_init_btn.fadeOut("fast", function() {
            parent.el.run_btn.fadeIn("fast").css("display","inline-block");
            parent.el.share_btn.fadeIn("fast").css("display","inline-block");
            parent.el.exit_btn.fadeIn("fast").css("display","inline-block");
            parent.el.cc_select_div.fadeIn("fast").css("display","inline-block");
            parent.el.pwr.fadeIn("fast").css("display","inline-block");
        });

        this.el.orig_code.fadeOut("fast", function() {
            parent.el.edited_code.fadeIn("fast");
        });
        this.el.orig_output.fadeOut("fast", function() {
            if (!parent.has_orig_output) {
                parent.el.output_p.fadeIn('fast');
            }
            parent.el.edited_output.fadeIn("fast", function() {
                parent.el.root.height('auto');
            });
        });

        this.is_orig = false;
    };

    this.restore_orig = function() {
        if (this.is_orig) {
            return; // already replaced
        }

        this.el.root.height(this.el.root.height());

        var parent = this;

        this.el.run_btn.fadeOut("fast", function() {
            parent.el.run_init_btn.fadeIn("fast").css("display","inline-block");
        });
        this.el.share_btn.fadeOut("fast");
        this.el.exit_btn.fadeOut("fast");
        this.el.cc_select_div.fadeOut("fast");
        this.el.pwr.fadeOut("fast");

        this.el.edited_code.fadeOut("fast", function() {
            parent.el.orig_code.fadeIn("fast");
        });

        this.el.compiler_output_p.fadeOut('fast');
        this.el.compiler_output.fadeOut('fast');

        if (!this.has_orig_output) {
            this.el.output_p.fadeOut('fast');
        }

        var parent = this;
        this.el.edited_output.fadeOut("fast", function() {
            parent.el.orig_output.fadeIn("fast", function() {
                parent.el.root.height('auto');
            });
        });

        this.is_orig = true;
    };

    this.enable_ui(true);
};

function get_script_cached(url, callback) {
    return $.ajax({
            type: "GET",
            url: url,
            success: callback,
            dataType: "script",
            cache: true
    });
};

window.highlight_error = function(node, b) {
    node.style.cursor = b ? 'pointer' : 'auto';
};

window.jump_to_error = function(node, lineno) {
    var root = $(node).parents('.t-example');
    if (root.length > 0) {
        for (var i = 0; i < editors.length; ++i) {
            if (editors[i].el.root.is(root)) {
                var editor = editors[i];
                editor.editor.gotoLine(lineno, 0, true);
                editor.editor.focus();
            }
        }
    }
};

var editors = [];

$.when(
    get_script_cached('http://d1n0x3qji82z53.cloudfront.net/src-min-noconflict/ace.js')
).done(function() {
    $.when(
        get_script_cached('http://d1n0x3qji82z53.cloudfront.net/src-min-noconflict/mode-c_cpp.js'),
        $.Deferred(function(deferred) {
            $(deferred.resolve);
        })
    ).done(function() {
        $('.t-example-live-link > a').each(function() {
            $(this).replaceWith('<div class="coliru-btn coliru-btn-run-init">Run this code</div>');
        });
        $('.t-example > .mw-geshi:first').each(function() {
            $(this).addClass('t-example-code');
        });

        $('.coliru-btn-run-init').click(function() {
            var root = $(this).parent().parent();

            // find the editor for this root element
            var i;
            for (i = 0; i < editors.length; ++i) {
                if (editors[i].el.root.is(root)) {
                    break;
                }
            }
            if (i == editors.length) {
                editors[i] = new Editor(root);
            }

            var editor = editors[i];
            editor.replace_orig();
            editor.compile_now();
        });
    });
});
