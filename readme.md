Репозитории, которые уже включены:

    BaseOS - основные системные пакеты
    AppStream - дополнительные приложения


Необходимо включить:

    PowerTools - важен для *-devel пакетов,
    EPEL - дополнительные пакеты

        dnf config-manager --set-enabled powertools
        dnf install -y epel-release
        dnf update -y

-----------------

Билдить нужно будет командой:

    QA_RPATHS=$(( 0x0001|0x0002|0x0010|0x0020 )) rpmbuild -ba openresty.spec

-----------------


После сборки и установки для теста можно проверить работу сервиса

    sudo dnf install -y ~/rpmbuild/RPMS/x86_64/openresty-1.25.3.2-1.el8.x86_64.rpm

    sudo systemctl status openresty

    sudo systemctl start openresty

    sudo systemctl status openresty

    sudo systemctl enable openresty

Для функционального тестирования:

    # Проверяем версию OpenResty
    /usr/local/openresty/bin/openresty -v

    # Тестируем конфигурацию
    sudo /usr/local/openresty/nginx/sbin/nginx -t -c /etc/openresty/openresty.conf

    # Проверяем, отвечает ли веб-сервер
    curl -I http://localhost/

    # Тестируем Lua функциональность
    curl http://localhost/lua

    # Проверяем страницу статуса
    curl http://localhost/nginx_status
