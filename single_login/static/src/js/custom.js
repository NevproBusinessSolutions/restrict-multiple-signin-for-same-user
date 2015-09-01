openerp.single_login = function (instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

setInterval(updateExpiry,60*1000);

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
};

function updateExpiry() {
    var on_login = document.getElementsByClassName('oe_login').length
    if (on_login == 0) {
        sid = getCookie('sid');
        new instance.web.Model("res.users").call("save_session",[sid]).done(function(data) {return data});
    }
};


instance.web.Session.include({
    session_authenticate: function(db, login, password, sid, _volatile) {
        var self = this;
        var base_location = document.location.protocol + '//' + document.location.host;
        var params = { db: db, login: login, password: password, base_location: base_location, sid: sid };
        return this.rpc("/web/session/authenticate", params).then(function(result) {
            if (!result.uid) {
                return $.Deferred().reject();
            }
            _.extend(self, result);
            if (!_volatile) {
                self.set_cookie('session_id', self.session_id);
            }
            return self.load_modules();
        });
    },
});


instance.web.WebClient.include({
    getCookie: function (key) {
        var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
        return keyValue ? keyValue[2] : null;
    },
    
    clear_session: function() {
        var self = this;
        //call res.users to clear user session
        new instance.web.Model('res.users').call('clear_session');
        document.cookie = [
            'sid=' + self.getCookie('sid'),
            'path=/',
            'max-age=0',
            'expires=' + new Date(new Date().getTime()).toGMTString()
        ].join(';');
    },
    
    on_logout: function() {
        var self = this;
        if (!this.has_uncommitted_changes()) {
            self.clear_session();
            this.session.session_logout().done(function () {
                $(window).unbind('hashchange', self.on_hashchange);
                self.do_push_state({});
                window.setTimeout(function(){location.reload()},200)
                //window.location.reload();
            });
        }
    },
});

instance.web.Login.include({
    remember_last_used_database: function(db) {
        // This cookie will be used server side in order to avoid db reloading on first visit
        var ttl = 2 * 60;
        document.cookie = [
            'last_used_database=' + db,
            'path=/',
            'max-age=' + ttl,
            'expires=' + new Date(new Date().getTime() + ttl * 1000).toGMTString()
        ].join(';');
    },
    
    getCookie: function (key) {
        var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
        return keyValue ? keyValue[2] : null;
    },
    
    do_login: function (db, login, password) {
        var self = this;
        self.valid_login = null;
        var sid = getCookie('sid');
        self.hide_error();
        self.$(".oe_login_pane").fadeOut("slow");
        
        return this.session.session_authenticate(db, login, password, sid).then(function() {
        self.remember_last_used_database(db);
        if (self.has_local_storage && self.remember_credentials) {
            localStorage.setItem(db + '|last_login', login);
            if (self.session.debug) {
                localStorage.setItem(db + '|last_password', password);
            }
        }
        new instance.web.Model("res.users").call("save_session",[sid]).then(function(data) {return data});
        self.trigger('login_successful');
        }, function () {
            self.$(".oe_login_pane").fadeIn("fast", function() {
                self.show_error("Login failed due to one of the following reasons","- Invalid username or password","- User already logged in from another system");
            });
        });
    },
    
    show_error: function(m1, m2, m3) {
        this.$el.addClass("oe_login_invalid");
        this.$(".oe_login_error_message").empty();
        this.$(".oe_login_error_message").append(
            "<div>"+m1+"</div><div>"+m2+"</div><div>"+m3+"</div>"
        );
    },
});

};