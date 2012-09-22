jackalope
=========

Mashing up taskrabbit and asana.

Overview:
--------
Jackalope is an interface between several Foreman services (who create and
assign tasks) and several Worker services (who do tasks). Each Jackalope Task
has a Foreman and Worker component to it.

Dependencies:
---------
Python wrapper for Asana API: https://github.com/pandemicsyn/asana
Python wrapper for OAuth2: https://github.com/liluo/py-oauth2
    pip install py-oauth2
