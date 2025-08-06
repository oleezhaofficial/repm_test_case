%define __os_install_post %{nil}

Name:           openresty
Version:        1.25.3.2
Release:        1%{?dist}
Summary:        Scalable Web Platform by Extending NGINX with Lua

License:        BSD
Group:          System Environment/Daemons
URL:            https://openresty.org/

Source0:        https://openresty.org/download/%{name}-%{version}.tar.gz
Source1:        openresty.service
Source2:        openresty.conf
Source3:        openresty.logrotate

BuildRequires:  gcc gcc-c++
BuildRequires:  make
BuildRequires:  pcre-devel >= 8.42
BuildRequires:  openssl-devel >= 1.1.1
BuildRequires:  zlib-devel
BuildRequires:  systemd-devel
BuildRequires:  readline-devel

Requires:       pcre >= 8.42
Requires:       openssl >= 1.1.1
Requires:       zlib
Requires:       systemd
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
OpenResty is a full-fledged web platform that integrates our enhanced version 
of the Nginx core, our enhanced version of LuaJIT, many carefully written 
Lua libraries, lots of high quality 3rd-party Nginx modules, and most of 
their external dependencies.


%prep
%autosetup -n %{name}-%{version}


%build
# --prefix задаёт базовую директорию установки
# --with-http_ssl_module включает поддержку SSL
# --with-http_v2_module включает поддержку HTTP/2
# --with-http_realip_module нужен для работы за прокси
# --with-http_gzip_static_module для статического сжатия
# --with-http_secure_link_module для защищённых ссылок
# --with-http_stub_status_module для мониторинга
# --with-luajit включает LuaJIT
# --with-file-aio включает асинхронный файловый I/O
./configure \
    --prefix=/usr/openresty \
    --with-http_ssl_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_gzip_static_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-luajit \
    --with-file-aio \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-threads \
    --with-compat \
    --without-http_redis2_module \
    --without-http_redis_module \
    --without-http_rds_json_module \
    --without-http_rds_csv_module

# Компилируем с использованием всех доступных ядер
make %{?_smp_mflags}

# Секция установки в временную директорию
%install
# Очищаем временную директорию установки
rm -rf %{buildroot}

# Устанавливаем OpenResty
make install DESTDIR=%{buildroot}

# Создаём необходимые директории для конфигурации и логов
mkdir -p %{buildroot}%{_sysconfdir}/openresty/conf.d
mkdir -p %{buildroot}%{_localstatedir}/log/openresty
mkdir -p %{buildroot}%{_localstatedir}/cache/openresty
mkdir -p %{buildroot}%{_localstatedir}/run/openresty
mkdir -p %{buildroot}/usr/openresty/nginx/logs
mkdir -p %{buildroot}/var/log/openresty



mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "/usr/openresty/luajit/lib" > %{buildroot}/etc/ld.so.conf.d/openresty.conf

# Устанавливаем systemd service файл
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/openresty.service

# Устанавливаем основной конфигурационный файл
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/openresty/openresty.conf

# Устанавливаем конфигурацию logrotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/openresty

# Создаём символические ссылки для удобства
mkdir -p %{buildroot}%{_bindir}
ln -sf /usr/openresty/bin/openresty %{buildroot}%{_bindir}/openresty
ln -sf /usr/openresty/nginx/sbin/nginx %{buildroot}%{_bindir}/openresty-nginx

# Скрипты, выполняемые при установке/удалении пакета

# Создание пользователя перед установкой
%pre
getent group openresty >/dev/null || groupadd -r openresty
getent passwd openresty >/dev/null || \
    useradd -r -g openresty -d /usr/openresty -s /sbin/nologin \
    -c "OpenResty web server" openresty
exit 0

# Активация systemd сервиса после установки
%post
/sbin/ldconfig
%systemd_post openresty.service

# Остановка сервиса перед удалением
%preun
%systemd_preun openresty.service

# Перезагрузка systemd после удаления
%postun
/sbin/ldconfig
%systemd_postun_with_restart openresty.service

# Список файлов, входящих в пакет
%files
# Основные файлы программы
/usr/openresty/
/etc/ld.so.conf.d/openresty.conf
%{_bindir}/openresty
%{_bindir}/openresty-nginx
%{_unitdir}/openresty.service
/usr/openresty/luajit/lib/libluajit-5.1.so*

# Конфигурационные файлы (config означает, что при обновлении
# пакета файлы не будут перезаписаны, если пользователь их изменил)
%config(noreplace) %{_sysconfdir}/openresty/openresty.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/openresty

# Директории для логов и кэша
%dir /usr/openresty/nginx/logs
%dir /var/run/openresty
%attr(755, root, root) /usr/openresty/luajit/lib/libluajit-5.1.so*
%attr(755, openresty, openresty) /usr/openresty/nginx/logs
%attr(0755,openresty,openresty) %dir %{_localstatedir}/log/openresty
%attr(0755,openresty,openresty) %dir %{_localstatedir}/cache/openresty
%attr(0755,openresty,openresty) %dir %{_localstatedir}/run/openresty
%dir %{_sysconfdir}/openresty
%dir %{_sysconfdir}/openresty/conf.d


%changelog
* Wed Aug 06 2025 Mikhail Dyachkov - 1.25.3.2-1
- Initial package for OpenResty 1.25.3.2
- Built for CentOS Stream 8
- Added systemd integration
- Added logrotate configuration
- Created dedicated openresty user