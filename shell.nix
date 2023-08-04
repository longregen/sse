{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  name = "cuda-env-shell";
  propagatedBuildInputs = with pkgs; [
    autoconf
    binutils
    cudatoolkit
    curl
    freeglut
    git
    gitRepo
    gnumake
    gnupg
    gperf
    gcc11
    linuxPackages.nvidia_x11
    m4
    ncurses5
    pam
    procps
    python310Packages.eventlet
    python310Packages.flask-socketio
    python310Packages.python-socketio
    python310Packages.gevent
    python310Packages.psycopg2
    python310Packages.pytorch-bin
    stdenv.cc
    stdenv.cc.cc.lib
    unzip
    utillinux
    xorg.libX11
    xorg.libXext
    xorg.libXi
    xorg.libXmu
    xorg.libXrandr
    xorg.libXv
    zlib
  ];
  shellHook = ''
    export CUDA_PATH=${pkgs.cudatoolkit}
    export EXTRA_LDFLAGS="-L/lib -L${pkgs.linuxPackages.nvidia_x11}/lib"
    export EXTRA_CCFLAGS="-I/usr/include"
    export CC="${pkgs.gcc11}/bin/gcc"
    export PATH="${pkgs.python311Packages.pytorch-bin}/bin/python:$PATH"
    source .venv/bin/activate
  '';
}
