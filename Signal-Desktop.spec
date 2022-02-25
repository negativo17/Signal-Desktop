%global debug_package %{nil}
# Build id links are sometimes in conflict with other RPMs.
%define _build_id_links none

# Remove bundled libraries from requirements/provides
%global __requires_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libvk_swiftshader\\.so.*|libvulkan\\.so.*)$
%global __provides_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libvk_swiftshader\\.so.*|libvulkan\\.so.*)$
%global __requires_exclude_from ^%{_libdir}/%{name}/resources/app.asar.unpacked/.*$
%global __provides_exclude_from ^%{_libdir}/%{name}/resources/app.asar.unpacked/.*$

#global beta beta.2

Name:       Signal-Desktop
Version:    5.33.0
Release:    1%{?dist}
Summary:    Private messaging from your desktop
License:    AGPLv3
URL:        https://signal.org/
BuildArch:  aarch64 x86_64

Source0:    https://github.com/signalapp/%{name}/archive/v%{version}%{?beta:-%{beta}}.tar.gz#/Signal-Desktop-%{version}%{?beta:-%{beta}}.tar.gz
Source1:    %{name}-wrapper
Source2:    %{name}.desktop
Patch0:     %{name}-fix-build.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  git-lfs
BuildRequires:  npm >= 16
BuildRequires:  openssl-devel
BuildRequires:  python3
BuildRequires:  yarnpkg

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
yarn install --ignore-engines
yarn generate
yarn build

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

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%doc LICENSE
%{_bindir}/signal-desktop
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_libdir}/%{name}

%changelog
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

* Thu Oct 28 2021 Simone Caronni <negativo17@gmail.com> - 5.22.0-1
- Update to 5.22.0.

* Tue Oct 26 2021 Simone Caronni <negativo17@gmail.com> - 5.21.0-1
- Update to 5.21.0.

* Fri Oct 15 2021 Simone Caronni <negativo17@gmail.com> - 5.20.0-1
- Update to 5.20.0.

* Wed Oct 06 2021 Simone Caronni <negativo17@gmail.com> - 5.19.0-1
- Update to 5.19.0.

* Tue Oct 05 2021 Simone Caronni <negativo17@gmail.com> - 5.18.1-1
- Update to 5.18.1.

* Mon Oct 04 2021 Simone Caronni <negativo17@gmail.com> - 5.18.0-1
- Update to 5.18.0.

* Fri Sep 17 2021 Simone Caronni <negativo17@gmail.com> - 5.17.2-1
- Update to 5.17.2.

* Sat Sep 11 2021 Simone Caronni <negativo17@gmail.com> - 5.17.1-1
- Update to 5.17.1.

* Thu Sep 09 2021 Simone Caronni <negativo17@gmail.com> - 5.17.0-1
- Update to 5.17.0.

* Mon Sep 06 2021 Simone Caronni <negativo17@gmail.com> - 5.16.0-1
- Update to 5.16.0.

* Thu Aug 26 2021 Simone Caronni <negativo17@gmail.com> - 5.15.0-1
- Update to 5.15.0.

* Thu Aug 19 2021 Simone Caronni <negativo17@gmail.com> - 5.14.0-1
- Update to 5.14.0.

* Mon Aug 16 2021 Simone Caronni <negativo17@gmail.com> - 5.13.1-1
- Update to 5.13.1.

* Thu Aug 12 2021 Simone Caronni <negativo17@gmail.com> - 5.13.0-2
- Update to 5.13.0 final.

* Wed Aug 11 2021 Simone Caronni <negativo17@gmail.com> - 5.13.0-1
- Update to 5.13.0-beta.2 due to issues with releases and versions in the
  5.12.x branch (release 5.12.2 contained 5.12.0-beta.1 code).

* Fri Aug 06 2021 Simone Caronni <negativo17@gmail.com> - 5.12.2-1
- Update to 5.12.2.

* Thu Aug 05 2021 Simone Caronni <negativo17@gmail.com> - 5.12.1-1
- Update to 5.12.1.

* Wed Aug 04 2021 Simone Caronni <negativo17@gmail.com> - 5.12.0-1
- Update to 5.12.0.

* Tue Jul 27 2021 Simone Caronni <negativo17@gmail.com> - 5.10.0-1
- Update to 5.10.0.
- Fix library filter.

* Sat Jun 26 2021 Simone Caronni <negativo17@gmail.com> - 5.6.2-1
- Update to 5.6.2.

* Sat Jun 05 2021 Simone Caronni <negativo17@gmail.com> - 5.4.0-1
- Update to 5.4.0.

* Fri Jun 04 2021 Simone Caronni <negativo17@gmail.com> - 5.3.0-1
- Update to 5.3.0.

* Sun May 23 2021 Simone Caronni <negativo17@gmail.com> - 5.2.1-1
- Update to 5.2.1.
- Clean up SPEC file.
