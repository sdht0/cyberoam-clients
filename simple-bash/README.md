Cyberoam login bash commands
============================

Easily manage cyberoam login/logout using the following commands

Log in
----------
`curl -k -d mode=191 -d username=username -d password=password https://172.16.1.1:8090/login.xml`

Acknowledge
-------------
`while [ 1 ];do curl -k -G -d mode=192 -d username=username https://172.16.1.1:8090/live; sleep 180; done`

End using `ctrl+c`

Log out
-----------
`curl -k -d mode=193 -d username=username https://172.16.1.1:8090/logout.xml`