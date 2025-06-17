# mock configuration:
# - Requires network for running yarn/electron build

%global debug_package %{nil}
# Build id links are sometimes in conflict with other RPMs.
%define _build_id_links none

# Remove bundled libraries from requirements/provides
%global __requires_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libvk_swiftshader\\.so.*|libvulkan\\.so.*)$
%global __provides_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libvk_swiftshader\\.so.*|libvulkan\\.so.*)$
%global __requires_exclude_from ^%{_libdir}/%{name}/resources/app.asar.unpacked/.*$
%global __provides_exclude_from ^%{_libdir}/%{name}/resources/app.asar.unpacked/.*$

#global beta beta.2

%global desktop_id org.signal.Signal

Name:       Signal-Desktop
Version:    7.57.0
Release:    1%{?dist}
Summary:    Private messaging from your desktop
License:    AGPLv3
URL:        https://signal.org/
BuildArch:  aarch64 x86_64

Source0:    https://github.com/signalapp/%{name}/archive/v%{version}%{?beta:-%{beta}}.tar.gz#/Signal-Desktop-%{version}%{?beta:-%{beta}}.tar.gz
Source1:    %{name}-wrapper
Source2:    %{desktop_id}.desktop
Source3:    %{desktop_id}.metainfo.xml
Patch0:     %{name}-fix-build.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  git-lfs
BuildRequires:  libappstream-glib
BuildRequires:  libxcrypt-compat
BuildRequires:  lzo
BuildRequires:  npm
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  python3

Requires:   libappindicator-gtk3
Requires:   libnotify

Provides:   signal-desktop = %{version}-%{release}
Obsoletes:  signal-desktop < %{version}-%{release}

%description
Millions of people use Signal every day for free and instantaneous communication
anywhere in the world. Send and receive high-fidelity messages, participate in
HD voice/video calls, and explore a growing set of new features that help you
stay connected. Signal’s advanced privacy-preserving technology is always
enabled, so you can focus on sharing the moments that matter with the people who
matter to you.

Signal Desktop is an Electron application that links with Signal on Android or
iOS.

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}

%build
mkdir -p ~/.local/bin
export PATH=$HOME/.local/bin/:$PATH

npm config set prefix '~/.local/'

PATH="$npm_global/bin:$PATH"
npm install -g pnpm@latest-10

pnpm install
pnpm run clean-transpile
cd sticker-creator
pnpm install
pnpm run build
cd ..
pnpm run generate
pnpm run prepare-beta-build
pnpm run build-linux

# Remove non-relevant binaries
rm -fr release/linux-unpacked/chrome_*.pak \
    crelease/linux-unpacked/hrome-sandbox \
    release/linux-unpacked/swiftshader

%install
# Main files
install -dm 755 %{buildroot}%{_libdir}/%{name}
install -dm 755 %{buildroot}%{_bindir}

cp -fr release/linux*unpacked/* %{buildroot}%{_libdir}/%{name}

# Icons
for size in 16 24 32 48 64 128 256 512 1024; do
  install -p -D -m 644 build/icons/png/${size}x${size}.png \
    %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/%{name}.png
done

# Wrapper script
mkdir -p %{buildroot}%{_bindir}
cat %{SOURCE1} | sed -e 's|INSTALL_DIR|%{_libdir}/%{name}|g' \
    > %{buildroot}%{_bindir}/signal-desktop
chmod +x %{buildroot}%{_bindir}/signal-desktop

# Desktop file
install -m 0644 -D -p %{SOURCE2} %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

# AppData file
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml
%if 0%{?rhel}
sed -i -e '/url type="contribute"/d' %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml
%endif

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml

%files
%doc LICENSE
%{_bindir}/signal-desktop
%{_datadir}/applications/%{desktop_id}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_metainfodir}/%{desktop_id}.metainfo.xml
%{_libdir}/%{name}

%changelog
* Tue Jun 17 2025 Simone Caronni <negativo17@gmail.com> - 7.57.0-1
- Update to 7.57.0.

* Mon Jun 09 2025 Simone Caronni <negativo17@gmail.com> - 7.56.1-1
- Update to 7.56.1.

* Thu May 29 2025 Simone Caronni <negativo17@gmail.com> - 7.56.0-1
- Update to 7.56.0.

* Thu May 22 2025 Simone Caronni <negativo17@gmail.com> - 7.55.0-1
- Update to 7.55.0.

* Wed May 14 2025 Simone Caronni <negativo17@gmail.com> - 7.54.0-1
- Update to 7.54.0.

* Wed May 07 2025 Simone Caronni <negativo17@gmail.com> - 7.53.0-1
- Update to 7.53.0.

* Thu Apr 24 2025 Simone Caronni <negativo17@gmail.com> - 7.52.0-1
- Update to 7.52.0.

* Sun Apr 13 2025 Simone Caronni <negativo17@gmail.com> - 7.50.0-1
- Update to 7.50.0.

* Thu Apr 03 2025 Simone Caronni <negativo17@gmail.com> - 7.49.0-1
- Update to 7.49.0.

* Mon Mar 31 2025 Simone Caronni <negativo17@gmail.com> - 7.48.0-1
- Update to 7.48.0.
- Require Node.js 22+.

* Fri Mar 21 2025 Simone Caronni <negativo17@gmail.com> - 7.47.0-1
- Update to 7.47.0.

* Sat Mar 08 2025 Simone Caronni <negativo17@gmail.com> - 7.45.1-1
- Update to 7.45.1.

* Wed Mar 05 2025 Simone Caronni <negativo17@gmail.com> - 7.45.0-1
- Update to 7.45.0.
- Trim changelog.
- Signal has switched to pnpm in place of npm.

* Fri Feb 28 2025 Simone Caronni <negativo17@gmail.com> - 7.44.0-1
- Update to 7.44.0.

* Sat Feb 22 2025 Simone Caronni <negativo17@gmail.com> - 7.43.0-1
- Update to 7.43.0.

* Thu Feb 13 2025 Simone Caronni <negativo17@gmail.com> - 7.42.0-1
- Update to 7.42.0.

* Sat Feb 08 2025 Simone Caronni <negativo17@gmail.com> - 7.41.0-1
- Update to 7.41.0.

* Tue Feb 04 2025 Simone Caronni <negativo17@gmail.com> - 7.40.1-1
- Update to 7.40.1.

* Tue Jan 28 2025 Simone Caronni <negativo17@gmail.com> - 7.39.0-1
- Update to 7.39.0.

* Sun Jan 19 2025 Simone Caronni <negativo17@gmail.com> - 7.38.0-1
- Update to 7.38.0.

* Fri Jan 10 2025 Simone Caronni <negativo17@gmail.com> - 7.37.0-1
- Update to 7.37.0.
