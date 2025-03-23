%define _disable_ld_no_undefined 1

# Following modules bring no additionnal dependencies
# Other ones go into separate packages
%define base_modules	mod_accesslog.so,mod_cgi.so,mod_dirlisting.so,mod_extforward.so,mod_proxy.so,mod_rrdtool.so,mod_ssi.so,mod_status.so,mod_userdir.so

Name:		lighttpd
Version:	1.4.78
Release:	1
Summary:	A fast webserver with minimal memory-footprint
License:	BSD
Group:		System/Servers
URL:		https://lighttpd.net/
Source0:	http://download.lighttpd.net/lighttpd/releases-1.4.x/%{name}-%{version}.tar.xz
Source1:	http://download.lighttpd.net/lighttpd/releases-1.4.x/%{name}-%{version}.tar.xz.asc
Source2:	lighttpd.service
Source3:	php.d-lighttpd.ini
Patch1:		lighttpd-defaultroot.patch
BuildRequires:	pkgconfig(libpcre2-posix)
BuildRequires:	attr-devel
Requires(post):  rpm-helper
Requires(post):	user(www)
Requires(preun): rpm-helper
# preserve installation of modules historically bundled with lighttpd package
Requires(post): %{name}-mod_deflate
Requires(post): %{name}-mod_openssl
Obsoletes:	%{name}-modules < %{EVRD}
Provides:	%{name}-modules = %{EVRD}
Provides:	webserver

%description
lighttpd (pronounced /lighty/) is a secure, fast, compliant, and very flexible
web server that has been optimized for high-performance environments. lighttpd
uses memory and CPU efficiently and has lower resource use than other popular
web servers. Its advanced feature-set (FastCGI, CGI, Auth, Output-Compression,
URL-Rewriting and much more) make lighttpd the perfect web server for all
systems, small and large.

This packages contains the server and base modules :
%(for mod in $(echo %base_modules | tr ',' '\n'); do echo ${mod%%.so}; done)

%package mod_auth
Summary:	Authentication module for %{name}
Group:		System/Servers
Requires:	%{name}
# preserve installation of modules historically bundled with lighttpd mod_auth
Requires(post): %{name}-mod_authn_ldap

%description mod_auth
lighttpd supports authentication methods described by RFC 7616 and RFC 7617:

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

%package mod_authn_ldap
Summary:	Authentication module for lighttpd that uses LDAP
Requires:	%{name}
BuildRequires:	pkgconfig(ldap)

%description mod_authn_ldap
Authentication module for lighttpd that uses LDAP.

%package mod_deflate
Summary:	Compression module for %{name}
Group:		System/Servers
Requires:	%{name}
BuildRequires:	pkgconfig(zlib)

%description mod_deflate
Compression module for lighttpd.

%package mod_webdav
Summary:	WebDAV module for %{name}
Group:		System/Servers
Requires:	%{name}
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(sqlite3)

%description mod_webdav
The WebDAV module for %{name} implementing RFC 4918.

%package mod_magnet
Summary:	Module to control the request handling in %{name}
Group:		System/Servers
Requires:	%{name}
BuildRequires:	lua-devel

%description mod_magnet
mod_magnet can attract a request in several stages in the request-handling.

* at the same level as mod_rewrite, before any parsing of the URL is done
* at a later stage, when the doc-root is known and the physical-path is
  already setup
* at response start, right before response headers are finalized

Keep in mind that the magnet is executed in the core of lighty. EVERY long-
running operation is blocking ALL connections in the server. You are warned.
For time-consuming or blocking scripts use mod_fastcgi and friends.

%package mod_openssl
Summary:	TLS module for lighttpd that uses OpenSSL
Requires:	%{name}
BuildRequires:	pkgconfig(openssl)

%description mod_openssl
TLS module for lighttpd that uses OpenSSL.

%package mod_vhostdb_ldap
Summary:	Virtual host module for lighttpd that uses LDAP
Requires:	%{name}
BuildRequires:	pkgconfig(ldap)

%description mod_vhostdb_ldap
Virtual host module for lighttpd that uses LDAP.

%package mod_vhostdb_mysql
Summary:	Virtual host module for lighttpd that uses MySQL
Requires:	%{name}
BuildRequires:	mysql-devel

%description mod_vhostdb_mysql
Virtual host module for lighttpd that uses MySQL.

%prep
%setup -q

%build
%configure --libdir=%{_libdir}/%{name}/ \
  --with-mysql\
  --with-ldap\
  --with-attr\
  --with-openssl\
  --with-pcre2\
  --with-webdav-props\
  --with-webdav-locks\
  --with-lua

%make_build

%install
%make_install

#install -Dm 644 doc/initscripts/sysconfig.lighttpd \
#    %{buildroot}%{_sysconfdir}/sysconfig/lighttpd

install -Dm 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service

install -Dm 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/php.d/lighttpd.ini

install -d -m 755 %{buildroot}%{_sysconfdir}/lighttpd
install -d -m 755 %{buildroot}%{_sysconfdir}/lighttpd/conf.d
install -m 644 doc/config/*.conf %{buildroot}%{_sysconfdir}/lighttpd
install -m 644 doc/config/conf.d/*.conf %{buildroot}%{_sysconfdir}/lighttpd/conf.d

install -d -m 755 %{buildroot}%{_logdir}/lighttpd

sed -i \
    -e 's!^server.username\s*=.*$!server.username = "apache"!;' \
    -e 's!^server.groupname\s*=.*$!server.groupname = "apache"!;' \
    -e 's!^var.server_root\s*=.*$!var.server_root = "/srv/www"!;' \
    -e 's!^server.document-root\s*=.*$!server.document-root = "/srv/www/html"!;' \
    -e 's!^server.errorlog\s*=.*$!server.errorlog = "%{_logdir}/lighttpd/error.log"!;' \
    %{buildroot}%{_sysconfdir}/lighttpd/lighttpd.annotated.conf

sed -i \
    -e 's!^accesslog.filename.*$!accesslog.filename = "%{_logdir}/lighttpd/access.log"!' \
    %{buildroot}%{_sysconfdir}/lighttpd/conf.d/access_log.conf


install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
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

echo %{_libdir}/%{name}/{%{base_modules}} | tr ' ' '\n' > base.list
for i in doc/outdated/*.txt
do
	mod=`cat "$i" | tr -d '\\r' | sed -n "s/^Module:.*\\(mod_.*\\)$/\\1/p"`
	if [ -z "$mod" ]
	then
		echo  "%doc $i" >> base.list
	else
		if echo "%{base_modules}" | grep "$mod" > /dev/null
		then
			echo "%doc $i" >> base.list
		else
			echo "%doc $i" >> "$mod"
		fi
	fi
done

%post
# Fix rights on logs after upgrade, else the server can not start
if [ $1 -gt 1 ]; then
	if grep '^server.username = "www"' %{_sysconfdir}/lighttpd/lighttpd.annotated.conf >/dev/null; then
		if [ `stat -c %U /var/log/lighttpd/` != "www" ]; then
			chown -R www /var/log/lighttpd/
		fi
	fi
fi

%files -f base.list
%doc doc/config/lighttpd.conf README NEWS COPYING AUTHORS
%doc doc/scripts/cert-staple.sh
%{_unitdir}/lighttpd.service
#config(noreplace) #{_sysconfdir}/sysconfig/lighttpd
%dir %{_sysconfdir}/lighttpd/
%dir %{_sysconfdir}/lighttpd/conf.d/
%exclude %{_sysconfdir}/lighttpd/conf.d/deflate.conf
%exclude %{_sysconfdir}/lighttpd/conf.d/magnet.conf
%exclude %{_sysconfdir}/lighttpd/conf.d/webdav.conf
%config(noreplace) %{_sysconfdir}/lighttpd/*.conf
%config(noreplace) %{_sysconfdir}/lighttpd/conf.d/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/php.d/lighttpd.ini
%attr(0755,www,www) %{_logdir}/lighttpd
%{_mandir}/*/*
%{_sbindir}/*
%{_libdir}/lighttpd/*.so
%exclude %{_libdir}/lighttpd/mod_auth.so
%exclude %{_libdir}/lighttpd/mod_authn_file.so
#%exclude %{_libdir}/lighttpd/mod_authn_dbi.so
#%exclude %{_libdir}/lighttpd/mod_authn_gssapi.so
%exclude %{_libdir}/lighttpd/mod_authn_ldap.so
#%exclude %{_libdir}/lighttpd/mod_authn_pam.so
#%exclude %{_libdir}/lighttpd/mod_authn_sasl.so
%exclude %{_libdir}/lighttpd/mod_deflate.so
#%exclude %{_libdir}/lighttpd/mod_gnutls.so
%exclude %{_libdir}/lighttpd/mod_magnet.so
#%exclude %{_libdir}/lighttpd/mod_maxminddb.so
#%exclude %{_libdir}/lighttpd/mod_mbedtls.so
%exclude %{_libdir}/lighttpd/mod_openssl.so
#%exclude %{_libdir}/lighttpd/mod_nss.so
#%exclude %{_libdir}/lighttpd/mod_vhostdb_dbi.so
%exclude %{_libdir}/lighttpd/mod_vhostdb_ldap.so
%exclude %{_libdir}/lighttpd/mod_vhostdb_mysql.so
#%exclude %{_libdir}/lighttpd/mod_vhostdb_pgsql.so

%files mod_auth -f mod_auth
%{_libdir}/%{name}/mod_auth.so
%{_libdir}/lighttpd/mod_authn_file.so

%files mod_authn_ldap
%{_libdir}/lighttpd/mod_authn_ldap.so

%files mod_deflate
%config(noreplace) %{_sysconfdir}/lighttpd/conf.d/deflate.conf
%{_libdir}/lighttpd/mod_deflate.so

%files mod_webdav
%config(noreplace) %{_sysconfdir}/lighttpd/conf.d/webdav.conf
%{_libdir}/%{name}/mod_webdav.so

%files mod_magnet
%config(noreplace) %{_sysconfdir}/lighttpd/conf.d/magnet.conf
%{_libdir}/%{name}/mod_magnet.so

%files mod_openssl
%{_libdir}/lighttpd/mod_openssl.so

%files mod_vhostdb_ldap
%{_libdir}/lighttpd/mod_vhostdb_ldap.so

%files mod_vhostdb_mysql
%{_libdir}/lighttpd/mod_vhostdb_mysql.so
