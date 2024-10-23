# app0-admin

Admin App for platform `app0`
Application Manager for Single SignOn & show available apps.

## Development

### Create a venv environment

```bash
python3.11 -m venv venv
source ./venv/bin/activate
```

Install dependencies & modules
```bash
make deps
make lock-requirements
```

Install development dependencies & modules
```bash
make install
make dev-deps
```
### Generate Open API spec & validate linting

To generate OpenApi Spec
```bash
make api
```

To validate linting
```bash
make qa
```

### Platform 1rst time setup

Go to: `http://localhost:8021/api/docs`

Run endpoint `setup-db` with `FORCE` keyword as parameter from API.

This should delete (if exist) and create all necessary collections and create some Test data:
- Superadmin: `superuser / abc123`

IMPORTANT: Remind disable setup-db endpoint after running it

### VS Code Debugging & Code style

- `/.vscode/launch.json`
- `/.vscode/settings.json`


# MS Windows specific installation details
* Open Visual Studio Code by running `code .` from an Anaconda prompt with environment `app0-admin` activated. Make sure to select the correct Python interpreter in Visual Studio Code.
* Download and install [Cygwin](https://www.cygwin.com/) for running bash scripts. Then, from a CMD prompt (not Powershell) with administrator privileges, create a symbolic link.
```bash
mklink /d "C:\bin" "C:\cygwin64\bin"
/bin/bash               #this should work
```
* Download and install [MS Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). Make sure to check "Desktop Development with C++" box in installation wizard.
* Replace every 'python3' occurrence with 'python' in these scripts
```bash
app0-admin/build/ci-static-app0-admin.sh
plugins/platform-auth/build/ci-static-plugins.sh
```
* If error `$'\r': command not found` occur, change line endings from CRLF to LF in these files:
```bash
app0-admin/build/ci-static-app0-admin.sh
plugins/platform-auth/build/ci-static-plugins.sh
update-openapi.sh
```

### Clean env, generate docker && publish to gitlab registry

```bash
rm -rf venv
rm requirements.lock
python3.11 -m venv venv
source ./venv/bin/activate
make deps
make lock-requirements
make build-docker
make publish-docker
```

### Sample users

DEF_SUPER = "superuser"
DEF_ADM_SP = "admin.sp@app0.me"
DEF_OP_SP = "operario.sp@app0.me"
DEF_PASSWORD1 = "abc123"
DEF_PASSWORD2 = "cde123"
DEF_PASSWORD1S = "pueingar3657"
DEF_PASSWORD2S = "starpla2023DASH."
