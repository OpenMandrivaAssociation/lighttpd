%define	name	lighttpd
%define	version	1.4.27
%define	release	%mkrel 1

# Following modules bring no additionnal dependencies
# Other ones go into separate packages
%define base_modules	mod_access.so,mod_accesslog.so,mod_alias.so,mod_cgi.so,mod_dirlisting.so,mod_evhost.so,mod_expire.so,mod_extforward.so,mod_fastcgi.so,mod_flv_streaming.so,mod_indexfile.so,mod_proxy.so,mod_redirect.so,mod_rewrite.so,mod_rrdtool.so,mod_scgi.so,mod_secdownload.so,mod_setenv.so,mod_simple_vhost.so,mod_ssi.so,mod_staticfile.so,mod_status.so,mod_userdir.so,mod_usertrack.so,mod_evasive.so

Name:		%name
Version:	%version
Release:	%release
Summary:	A fast webserver with minimal memory-footprint
Source0:	http://download.lighttpd.net/lighttpd/releases-1.4.x/%{name}-%{version}.tar.bz2
Source1:	lighttpd.init
License:	BSD
Group:		System/Servers
URL:		http://lighttpd.net/
BuildRequires:	zlib-devel fam-devel mysql-devel memcache-devel lua-devel
BuildRequires:	openssl-devel gdbm-devel bzip2-devel pcre-devel openldap-devel
BuildRequires:	attr-devel libxml2-devel sqlite3-devel
BuildRequires:	autoconf2.5
# For /var/www/html, we should split it
Requires(pre):	apache-conf
Requires:	apache-conf
Requires(post):	apache-conf
Requires(post):	rpm-helper
Requires(preun):rpm-helper
Obsoletes:	%name-modules
Provides:	%name-modules
Provides:	webserver
BuildRoot:	%{_tmppath}/%{name}-root

%description
Security, speed, compliance, and flexibility--all of these describe LightTPD
which is rapidly redefining efficiency of a webserver; as it is designed and
optimized for high performance environments. With a small memory
footprint compared to other web-servers, effective management of the
cpu-load, and advanced feature set (FastCGI, CGI, Auth,
Output-Compression, URL-Rewriting and many more) LightTPD is the
perfect solution for every server that is suffering load problems.

This packages contains the server and base modules :
%(for mod in $(echo %base_modules | tr ',' '\n'); do echo ${mod%%.so}; done)

%package mod_auth
Summary:	Authentification module for %{name}
Group:		System/Servers
Requires:	%{name}

%description mod_auth
lighttpd supportes both authentication method described by RFC 2617:

 - basic
 - digest

Depending on the method lighttpd provides various way to store the credentials
used for the authentication.

for basic auth:
 - plain
 - htpasswd
 - htdigest
 - ldap

for digest auth:
 - plain
 - htdigest

%package mod_cml
Summary:        CML (Cache Meta Language) module for %{name}
Group:          System/Servers
Requires:	%{name}

%description mod_cml
CML (Cache Meta Language) is a Meta language to describe the dependencies
of a page at one side and building a page from its fragments on the other side
using LUA.

%package mod_compress
Summary:        Output Compression module for %{name}
Group:          System/Servers
Requires:	%{name}

%description mod_compress
Output compression reduces the network load and can improve the
overall throughput of the webserver. All major http-clients support
compression by announcing it in the Accept-Encoding header. This
is used to negotiate the most suitable compression method.
We support deflate, gzip and bzip2.

%package mod_mysql_vhost
Summary:        MySQL-based vhosting module for %{name}
Group:          System/Servers
Requires:	%{name}

%description mod_mysql_vhost
With MySQL-based vhosting you can store the path to a given
host's document root in a MySQL database.

%package mod_trigger_b4_dl
Summary:        Trigger before Download module for %{name}
Group:          System/Servers
Requires:	%{name}

%description mod_trigger_b4_dl
Anti Hotlinking:
 - if user requests ''download-url'' directly, the request is denied
   and he is redirected to ''deny-url'
 - if user visits ''trigger-url'' before requesting ''download-url'',
    access is granted
 - if user visits ''download-url'' again after ''trigger-timeout'' has
   elapsed, the request is denied and he is redirected to ''deny-url''

The trigger information is either stored locally in a gdbm file or
remotely in memcached.

%package mod_webdav
Summary:        WebDAV module for %{name}
Group:          System/Servers
Requires:	%{name}

%description mod_webdav
The WebDAV module for %{name} is a very minimalistic implementation of RFC
2518.

%package mod_magnet
Summary:	Module to control the request handling in %{name}
Group:		System/Servers
Requires:	%{name}

%description mod_magnet
mod_magnet can attract a request in several stages in the request-handling.

* either at the same level as mod_rewrite, before any parsing of the URL is
  done
* or at a later stage, when the doc-root is known and the physical-path is
  already setup

Keep in mind that the magnet is executed in the core of lighty. EVERY long-
running operation is blocking ALL connections in the server. You are warned.
For time-consuming or blocking scripts use mod_fastcgi and friends.

%prep
%setup -q

%build
%configure2_5x --libdir=%{_libdir}/%{name}/ \
  --with-mysql\
  --with-ldap\
  --with-attr\
  --with-openssl\
  --with-pcre\
  --with-bzip2\
  --with-fam\
  --with-webdav-props\
  --with-gdbm\
  --with-memcache\
  --with-lua

%make

%install
rm -rf %buildroot
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}/{init.d,sysconfig}
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/init.d/lighttpd
install -m 644 doc/initscripts/sysconfig.lighttpd %{buildroot}%{_sysconfdir}/sysconfig/lighttpd

mkdir -p %{buildroot}%{_sysconfdir}/lighttpd
install -m 644 doc/config/lighttpd.conf %{buildroot}%{_sysconfdir}/lighttpd

sed -i 's£^server.document-root.*$£server.document-root = "%{_var}/www/html"£' %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.conf
sed -i 's£^server.errorlog.*$£server.errorlog = "%{_logdir}/lighttpd/error.log"£' %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.conf
sed -i 's£^accesslog.filename.*$£accesslog.filename = "%{_logdir}/lighttpd/access.log"£' %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.conf

sed -i 's£.*server.username[\t ]*= .*$£server.username = "apache"£' %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.conf
sed -i 's£.*server.groupname[\t ]*= .*$£server.groupname = "apache"£' %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.conf

mkdir -p %{buildroot}%{_logdir}/lighttpd

mkdir -p %{buildroot}%{_var}/www/html

mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} <<EOF
%{_logdir}/%{name}/*.log {
    size=20M
    rotate 5
    weekly
    missingok
    notifempty
    postrotate
        service %{name} reload
    endscript
}
EOF

rm -f %{buildroot}%{_libdir}/%{name}/*.la

echo %{_libdir}/%{name}/{%{base_modules}} | tr ' ' '\n' > base.list
for i in doc/*.txt
do
	mod=`cat "$i" | tr -d '\\r' | sed -n "s/^Module:.*\\(mod_.*\\)$/\\1/p"`
	if [ -z "$mod" ]
	then
		echo "%doc $i" >> base.list
	else
		if echo "%{base_modules}" | grep "$mod" > /dev/null
		then
			echo "%doc $i" >> base.list
		else
			echo "%doc $i" >> "$mod"
		fi
	fi
done

mkdir -p %buildroot%{_var}/www/html

%clean
rm -rf %buildroot

%post
# Fix rights on logs after upgrade, else the server can not start
if [ $1 -gt 1 ]; then
	if grep '^server.username = "apache"' %{_sysconfdir}/lighttpd/lighttpd.conf >/dev/null; then
		if [ `stat -c %U /var/log/lighttpd/` != "apache" ]; then
			chown -R apache /var/log/lighttpd/
		fi
	fi
fi

%_post_service lighttpd

%preun
%_preun_service lighttpd

%files -f base.list
%defattr(-,root,root)
%doc doc/config/lighttpd.conf README INSTALL NEWS COPYING AUTHORS
%attr(0755,root,root) %{_sysconfdir}/init.d/lighttpd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/lighttpd
%dir %{_sysconfdir}/lighttpd/
%config(noreplace) %{_sysconfdir}/lighttpd/*
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,apache,apache) %{_logdir}/lighttpd
%{_mandir}/*/*
%{_sbindir}/*
%attr(0755,apache,apache) %dir %{_var}/www
%attr(0755,root,root) %dir %{_var}/www/html

%files mod_auth -f mod_auth
%defattr(-,root,root)
%{_libdir}/%{name}/mod_auth.so

%files mod_cml -f mod_cml
%defattr(-,root,root)
%{_libdir}/%{name}/mod_cml.so

%files mod_compress -f mod_compress
%defattr(-,root,root)
%{_libdir}/%{name}/mod_compress.so

%files mod_mysql_vhost -f mod_mysql_vhost
%defattr(-,root,root)
%{_libdir}/%{name}/mod_mysql_vhost.so

%files mod_trigger_b4_dl -f mod_trigger_b4_dl
%defattr(-,root,root)
%{_libdir}/%{name}/mod_trigger_b4_dl.so

%files mod_webdav -f mod_webdav
%defattr(-,root,root)
%{_libdir}/%{name}/mod_webdav.so

%files mod_magnet -f mod_magnet
%defattr(-,root,root)
%{_libdir}/%{name}/mod_magnet.so


