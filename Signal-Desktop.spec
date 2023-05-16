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
Version:    6.17.1
Release:    1%{?dist}
Summary:    Private messaging from your desktop
License:    AGPLv3
URL:        https://signal.org/
BuildArch:  aarch64 x86_64

Source0:    https://github.com/signalapp/%{name}/archive/v%{version}%{?beta:-%{beta}}.tar.gz#/Signal-Desktop-%{version}%{?beta:-%{beta}}.tar.gz
Source1:    %{name}-wrapper
Source2:    %{name}.desktop
Source3:    %{desktop_id}.metainfo.xml
Patch0:     %{name}-fix-build.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  git-lfs
BuildRequires:  libappstream-glib
%if 0%{?fedora}
BuildRequires:  libxcrypt-compat
%endif
BuildRequires:  lzo
BuildRequires:  python3
BuildRequires:  yarnpkg

%if 0%{?fedora} >= 37
BuildRequires:  nodejs-npm
%else
BuildRequires:  npm
%endif

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
# Use a huge timeout for aarch64 builds
yarn install --ignore-engines --network-timeout 1000000
yarn generate
yarn build:release --dir

# Remove non-relevant binaries
pushd release/linux-*unpacked/

rm -fr chrome_*.pak chrome-sandbox swiftshader
find . -type f -depth -name "*.dylib" -delete
find . -type d -depth -name "win32*" -exec rm -fr {} \;
find . -type d -depth -name "darwin*" -exec rm -fr {} \;
%ifarch x86_64
find . -type d -depth -name "linux-arm64" -exec rm -fr {} \;
%else
find . -type d -depth -name "linux-x64" -exec rm -fr {} \;
%endif

popd

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
install -m 0644 -D -p %{SOURCE2} %{buildroot}%{_datadir}/applications/%{name}.desktop

# AppData file
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml

%files
%doc LICENSE
%{_bindir}/signal-desktop
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_metainfodir}/%{desktop_id}.metainfo.xml
%{_libdir}/%{name}

%changelog
* Tue May 16 2023 Simone Caronni <negativo17@gmail.com> - 6.17.1-1
- Update to 6.17.1.

* Wed May 10 2023 Simone Caronni <negativo17@gmail.com> - 6.17.0-1
- Update to 6.17.0.

* Thu Apr 27 2023 Simone Caronni <negativo17@gmail.com> - 6.16.0-1
- Update to 6.16.0.

* Mon Apr 10 2023 Simone Caronni <negativo17@gmail.com> - 6.13.0-1
- Update to 6.13.0.

* Thu Mar 30 2023 Simone Caronni <negativo17@gmail.com> - 6.12.0-1
- Update to 6.12.0.

* Tue Mar 28 2023 Simone Caronni <negativo17@gmail.com> - 6.11.0-2
- Adjust requirements for npm again.

* Sun Mar 26 2023 Simone Caronni <negativo17@gmail.com> - 6.11.0-1
- Update to 6.11.0.

* Tue Mar 21 2023 Simone Caronni <negativo17@gmail.com> - 6.10.1-2
- Trim changelog.
- Adjust requirements for npm and provide an explanation.

* Mon Mar 20 2023 Simone Caronni <negativo17@gmail.com> - 6.10.1-1
- Update to 6.10.1.

* Thu Mar 02 2023 Simone Caronni <negativo17@gmail.com> - 6.8.0-1
- Update to 6.8.0.

* Fri Feb 24 2023 Simone Caronni <negativo17@gmail.com> - 6.7.0-1
- Update to 6.7.0.

* Fri Feb 10 2023 Simone Caronni <negativo17@gmail.com> - 6.5.0-1
- Update to 6.5.0.

* Fri Feb 03 2023 Simone Caronni <negativo17@gmail.com> - 6.4.1-1
- Update to 6.4.1.

* Thu Jan 26 2023 Simone Caronni <negativo17@gmail.com> - 6.3.0-1
- Update to 6.3.0.

* Thu Jan 12 2023 Simone Caronni <negativo17@gmail.com> - 6.2.0-1
- Update to 6.2.0.

* Fri Dec 16 2022 Simone Caronni <negativo17@gmail.com> - 6.1.0-1
- Update to 6.1.0.

* Tue Dec 06 2022 Simone Caronni <negativo17@gmail.com> - 6.0.1-1
- Update to 6.0.1.

* Sun Dec 04 2022 Simone Caronni <negativo17@gmail.com> - 6.0.0-1
- Update to 6.0.0.

* Thu Nov 10 2022 Simone Caronni <negativo17@gmail.com> - 5.63.1-1
- Update to 5.63.1.

* Mon Nov 07 2022 Simone Caronni <negativo17@gmail.com> - 5.63.0-1
- Update to 5.63.0.

* Sun Oct 30 2022 Simone Caronni <negativo17@gmail.com> - 5.62.0-2
- Add note about mock configuration.
- Trim changelog.
- Increase timeout for aarch64 builds.
- Reduce patching, skip useless steps and make it work with Node.js packages in
  main distribution.
- Add AppData.

* Thu Oct 06 2022 Simone Caronni <negativo17@gmail.com> - 5.62.0-1
- Update to 5.62.0.
