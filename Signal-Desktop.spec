# mock configuration:
# - Requires network for running npm/electron build

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
Version:    7.88.0
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
BuildRequires:  pnpm
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  python3

Requires:   libappindicator-gtk3
Requires:   libnotify

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
pnpm install
pnpm run clean-transpile
cd sticker-creator
pnpm install
pnpm run build
cd ..
pnpm run generate
pnpm run prepare-beta-build
pnpm run build-linux

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
* Thu Feb 05 2026 Simone Caronni <negativo17@gmail.com> - 7.88.0-1
- Update to 7.88.0.
- Use packaged pnpm.
- SPEC file cleanup.

* Mon Feb 02 2026 Simone Caronni <negativo17@gmail.com> - 7.87.0-1
- Update to 7.87.0.

* Fri Jan 23 2026 Simone Caronni <negativo17@gmail.com> - 7.86.0-1
- Update to 7.86.0.

* Thu Jan 15 2026 Simone Caronni <negativo17@gmail.com> - 7.85.0-1
- Update to 7.85.0.

* Fri Jan 09 2026 Simone Caronni <negativo17@gmail.com> - 7.84.0-1
- Update to 7.84.0.

* Fri Dec 19 2025 Simone Caronni <negativo17@gmail.com> - 7.83.0-1
- Update to 7.83.0.

* Fri Dec 12 2025 Simone Caronni <negativo17@gmail.com> - 7.82.0-1
- Update to 7.82.0.

* Thu Dec 04 2025 Simone Caronni <negativo17@gmail.com> - 7.81.0-1
- Update to 7.81.0.

* Wed Nov 26 2025 Simone Caronni <negativo17@gmail.com> - 7.80.1-1
- Update to 7.80.1.

* Thu Nov 20 2025 Simone Caronni <negativo17@gmail.com> - 7.80.0-1
- Update to 7.80.0.

* Fri Nov 14 2025 Simone Caronni <negativo17@gmail.com> - 7.79.0-1
- Update to 7.79.0.

* Sun Nov 09 2025 Simone Caronni <negativo17@gmail.com> - 7.78.0-1
- Update to 7.78.0.
