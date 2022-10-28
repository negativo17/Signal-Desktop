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
Version:    5.62.0
Release:    2%{?dist}
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
BuildRequires:  lzo
BuildRequires:  npm >= 16
BuildRequires:  python3
BuildRequires:  yarnpkg

%if 0%{?fedora}
BuildRequires:  libxcrypt-compat
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
pushd release/linux-unpacked/

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

cp -fr release/linux-unpacked/* %{buildroot}%{_libdir}/%{name}

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
* Sun Oct 30 2022 Simone Caronni <negativo17@gmail.com> - 5.62.0-2
- Add note about mock configuration.
- Trim changelog.
- Increase timeout for aarch64 builds.
- Reduce patching, skip useless steps and make it work with Node.js packages in
  main distribution.
- Add AppData.

* Thu Oct 06 2022 Simone Caronni <negativo17@gmail.com> - 5.62.0-1
- Update to 5.62.0.

* Wed Oct 05 2022 Simone Caronni <negativo17@gmail.com> - 5.61.1-1
- Update to 5.61.1.

* Thu Sep 29 2022 Simone Caronni <negativo17@gmail.com> - 5.61.0-1
- Update to 5.61.0.

* Sun Sep 25 2022 Simone Caronni <negativo17@gmail.com> - 5.60.0-1
- Update to 5.60.0.

* Wed Sep 21 2022 Simone Caronni <negativo17@gmail.com> - 5.59.0-1
- Update to 5.59.0.

* Sun Sep 04 2022 Simone Caronni <negativo17@gmail.com> - 5.57.0-1
- Update to 5.57.0.

* Fri Aug 26 2022 Simone Caronni <negativo17@gmail.com> - 5.56.0-1
- Update to 5.56.0.

* Thu Aug 18 2022 Simone Caronni <negativo17@gmail.com> - 5.55.0-1
- Update to 5.55.0.

* Wed Aug 10 2022 Simone Caronni <negativo17@gmail.com> - 5.54.0-1
- Update to 5.54.0.

* Mon Aug 08 2022 Simone Caronni <negativo17@gmail.com> - 5.53.0-1
- Update to 5.53.0.

* Fri Jul 22 2022 Simone Caronni <negativo17@gmail.com> - 5.51.0-1
- Update to 5.51.0.

* Tue Jul 19 2022 Simone Caronni <negativo17@gmail.com> - 5.50.1-1
- Update to 5.50.1.

* Sat Jul 09 2022 Simone Caronni <negativo17@gmail.com> - 5.49.0-1
- Update to 5.49.0.

* Wed Jul 06 2022 Simone Caronni <negativo17@gmail.com> - 5.48.0-2
- Re-enable GPU acceleration, it works now with the updated bundled Electron

* Tue Jul 05 2022 Simone Caronni <negativo17@gmail.com> - 5.48.0-1
- Update to 5.48.0.

* Fri Jun 24 2022 Simone Caronni <negativo17@gmail.com> - 5.47.0-1
- Update to 5.47.0.

* Fri Jun 17 2022 Simone Caronni <negativo17@gmail.com> - 5.46.0-1
- Update to 5.46.0.

* Sun Jun 12 2022 Simone Caronni <negativo17@gmail.com> - 5.45.1-1
- Update to 5.45.1.

* Thu Jun 02 2022 Simone Caronni <negativo17@gmail.com> - 5.45.0-1
- Update to 5.45.0.

* Sat May 14 2022 Simone Caronni <negativo17@gmail.com> - 5.43.0-1
- Update to 5.43.0.

* Thu May 05 2022 Simone Caronni <negativo17@gmail.com> - 5.42.0-1
- Update to 5.42.0.

* Sun May 01 2022 Simone Caronni <negativo17@gmail.com> - 5.41.0-1
- Update to 5.41.0.

* Sun Apr 17 2022 Simone Caronni <negativo17@gmail.com> - 5.39.0-1
- Update to 5.39.0.

* Thu Mar 24 2022 Simone Caronni <negativo17@gmail.com> - 5.36.0-1
- Update to 5.36.0.

* Thu Mar 10 2022 Simone Caronni <negativo17@gmail.com> - 5.35.0-1
- Update to 5.35.0.

* Sun Mar 06 2022 Simone Caronni <negativo17@gmail.com> - 5.34.0-1
- Update to 5.34.0.

* Fri Feb 25 2022 Simone Caronni <negativo17@gmail.com> - 5.33.0-1
- Update to 5.33.0

* Wed Feb 16 2022 Simone Caronni <negativo17@gmail.com> - 5.31.1-1
- Update to 5.31.1.

* Thu Feb 03 2022 Simone Caronni <negativo17@gmail.com> - 5.30.0-1
- Update to 5.30.0.

* Wed Jan 26 2022 Simone Caronni <negativo17@gmail.com> - 5.29.1-1
- Update to 5.29.1.

* Fri Jan 21 2022 Simone Caronni <negativo17@gmail.com> - 5.29.0-1
- Update to 5.29.0.

* Thu Jan 13 2022 Simone Caronni <negativo17@gmail.com> - 5.28.0-1
- Update to 5.28.0.

* Mon Jan 10 2022 Simone Caronni <negativo17@gmail.com> - 5.27.1-1
- Update to 5.27.1.

* Wed Dec 15 2021 Simone Caronni <negativo17@gmail.com> - 5.26.0-1
- Update to 5.26.0.

* Mon Dec 13 2021 Simone Caronni <negativo17@gmail.com> - 5.25.1-2
- Fix build id links in conflict with other RPMs.

* Thu Dec 09 2021 Simone Caronni <negativo17@gmail.com> - 5.25.1-1
- Update to 5.25.1.

* Sun Nov 21 2021 Simone Caronni <negativo17@gmail.com> - 5.24.0-2
- Add wrapper script, fixes crash on Intel GPUs.
- Trim changelog.

* Thu Nov 18 2021 Simone Caronni <negativo17@gmail.com> - 5.24.0-1
- Update to 5.24.0.

* Wed Nov 10 2021 Simone Caronni <negativo17@gmail.com> - 5.23.1-1
- Update to 5.23.1.

* Thu Nov 04 2021 Simone Caronni <negativo17@gmail.com> - 5.23.0-1
- Update to 5.23.0.
