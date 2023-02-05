# Installing Requirements

## Requirements

To get started, you'll need these software installed:

- [Git](https://git-scm.com/)
- [Python 3](https://www.python.org/) (Python 3.11 is what the codebase uses)
- [Poetry](https://python-poetry.org/)
- [Pyenv](https://github.com/pyenv/pyenv) (Optional, Recommended)
- [WSL2](https://docs.microsoft.com/en-us/windows/wsl/) (If working on Windows)
- [Docker](https://www.docker.com/) (Use [Docker Engine](https://docs.docker.com/engine/) on Linux, [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows/WSL2, MacOS and Linux (beta))
- Discord Account + Discord App

> **Note**
> Rin is natively developed on Linux. This means that you must have a good understanding on how to use Linux in the terminal. It is recommended to use Ubuntu to start with, but more advanced users may feel more comfortable with other distros such as Arch. If you are using Windows, you must use WSL2.

## Development Prerequisites

These are the prerequisites packages for development

### Debian/Ubuntu

```sh 
sudo apt-get install libffi-dev python3-dev libnacl-dev libopus-dev libopus0 libopusenc-dev build-essentials \
libssl-dev curl wget git
```

> **Note**
> `uvloop` depends on shared libs from OpenSSL 1.1. You'll need to use the backport versions for Ubuntu 22.04 and higher

### RHEL/CentOS/Fedora 22 or below

```sh
sudo yum install make gcc libffi-devel python-devel \
openssl-devel opus-devel opus curl wget git
```
### Fedora 23+

```sh
sudo dnf install make automake gcc gcc-c++ kernel-devel \
libffi-devel python3-libnacl python3.11-devel openssl11-devel \
openssl-devel opus opus-devel curl wget git
```

### OpenSUSE

```sh
sudo zypper install gcc make automake openssl-devel openssl-1_1  \
libffi-devel python311-devel python311-libnacl opus libopus0 wget git curl
```

### Arch

```sh
sudo pacman -S --needed base-devel openssl openssl-1.1 libffi python python-libnacl opus
```

### MacOS/Homebrew

```sh
brew install openssl openssl@1.1 libffi git curl make opus
```

## Development Setup

1. Fork and clone the repo

    ```sh
    git clone https://github.com/[username]/Rin.git && cd Rin
    ```

    Or if you have the `gh` cli tool installed:

    ```sh
    gh repo clone [username]/Rin
    ```


2. Install all of the dependencies (including dev dependencies)

    ```sh
    poetry install --with=dev
    ```