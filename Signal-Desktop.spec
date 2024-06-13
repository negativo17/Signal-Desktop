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
Version:    7.12.0
Release:    1%{?dist}
Summary:    Private messaging from your desktop
License:    AGPLv3
URL:        https://signal.org/
BuildArch:  aarch64 x86_64

Source0:    https://github.com/signalapp/%{name}/archive/v%{version}%{?beta:-%{beta}}.tar.gz#/Signal-Desktop-%{version}%{?beta:-%{beta}}.tar.gz
Source1:    %{name}-wrapper
Source2:    %{name}.desktop
Source3:    https://raw.githubusercontent.com/flathub/%{desktop_id}/master/%{desktop_id}.metainfo.xml
Patch0:     %{name}-fix-build.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  git-lfs
BuildRequires:  libappstream-glib
BuildRequires:  lzo
BuildRequires:  python3
BuildRequires:  yarnpkg

%if 0%{?fedora}
BuildRequires:  libxcrypt-compat
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
mkdir -p .config/yarn/global
mv .yarnclean .config/yarn/global
# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
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
%if 0%{?rhel}
sed -i -e '/url type="contribute"/d' %{buildroot}%{_metainfodir}/%{desktop_id}.metainfo.xml
%endif

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
* Thu Jun 13 2024 Simone Caronni <negativo17@gmail.com> - 7.12.0-1
- Update to 7.12.0.

* Thu Jun 06 2024 Simone Caronni <negativo17@gmail.com> - 7.11.1-1
- Update to 7.11.1.

* Thu May 30 2024 Simone Caronni <negativo17@gmail.com> - 7.11.0-1
- Update to 7.11.0.

* Thu May 23 2024 Simone Caronni <negativo17@gmail.com> - 7.10.0-1
- Update to 7.10.0.

* Thu May 16 2024 Simone Caronni <negativo17@gmail.com> - 7.9.0-1
- Update to 7.9.0.

* Tue May 14 2024 Simone Caronni <negativo17@gmail.com> - 7.8.0-1
- Update to 7.8.0.

* Sat May 04 2024 Simone Caronni <negativo17@gmail.com> - 7.7.0-1
- Update to 7.7.0.

* Sat Apr 27 2024 Simone Caronni <negativo17@gmail.com> - 7.6.0-1
- Update to 7.6.0.

* Tue Apr 23 2024 Simone Caronni <negativo17@gmail.com> - 7.5.1-1
- Update to 7.5.1.

* Tue Apr 02 2024 Simone Caronni <negativo17@gmail.com> - 7.4.0-1
- Update to 7.4.0.

* Tue Mar 19 2024 Simone Caronni <negativo17@gmail.com> - 7.2.1-1
- Update to 7.2.1.

* Sat Mar 16 2024 Simone Caronni <negativo17@gmail.com> - 7.2.0-1
- Update to 7.2.0.

* Thu Mar 07 2024 Simone Caronni <negativo17@gmail.com> - 7.1.1-1
- Update to 7.1.1.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 7.0.0-1
- Update to 7.0.0.

* Thu Feb 22 2024 Simone Caronni <negativo17@gmail.com> - 6.48.1-1
- Update to 6.48.1.

* Thu Feb 22 2024 Simone Caronni <negativo17@gmail.com> - 6.48.0-1
- Update to 6.48.0.

* Sat Feb 17 2024 Simone Caronni <negativo17@gmail.com> - 6.47.1-1
- Update to 6.47.1.

* Fri Feb 09 2024 Simone Caronni <negativo17@gmail.com> - 6.47.0-1
- Update to 6.47.0.

* Mon Feb 05 2024 Simone Caronni <negativo17@gmail.com> - 6.46.0-1
- Update to 6.46.0.

* Wed Jan 31 2024 Simone Caronni <negativo17@gmail.com> - 6.45.1-1
- Update to 6.45.1.

* Thu Jan 25 2024 Simone Caronni <negativo17@gmail.com> - 6.45.0-1
- Update to 6.45.0.

* Thu Jan 18 2024 Simone Caronni <negativo17@gmail.com> - 6.44.1-1
- Update to 6.44.1.

* Tue Jan 16 2024 Simone Caronni <negativo17@gmail.com> - 6.44.0-1
- Update to 6.44.0.

* Wed Jan 10 2024 Simone Caronni <negativo17@gmail.com> - 6.43.2-1
- Update to 6.43.2.

* Sat Jan 06 2024 Simone Caronni <negativo17@gmail.com> - 6.43.1-1
- Update to 6.43.1.

* Thu Dec 28 2023 Simone Caronni <negativo17@gmail.com> - 6.42.1-1
- Update to 6.42.1.

* Fri Dec 15 2023 Simone Caronni <negativo17@gmail.com> - 6.42.0-1
- Update to 6.42.0.

* Thu Dec 07 2023 Simone Caronni <negativo17@gmail.com> - 6.41.0-1
- Update to 6.41.0.

* Thu Nov 30 2023 Simone Caronni <negativo17@gmail.com> - 6.40.0-1
- Update to 6.40.0.

* Sun Nov 26 2023 Simone Caronni <negativo17@gmail.com> - 6.39.1-1
- Update to 6.39.1.

* Thu Nov 16 2023 Simone Caronni <negativo17@gmail.com> - 6.39.0-1
- Update to 6.39.0.

* Thu Nov 09 2023 Simone Caronni <negativo17@gmail.com> - 6.38.0-1
- Update to 6.38.0.

* Thu Nov 02 2023 Simone Caronni <negativo17@gmail.com> - 6.37.0-1
- Update to 6.37.0.
- Update node-gyp to fix Python 3.12 / Fedora 39 builds.

* Fri Oct 20 2023 Simone Caronni <negativo17@gmail.com> - 6.35.0-1
- Update to 6.35.0.

* Tue Oct 17 2023 Simone Caronni <negativo17@gmail.com> - 6.34.1-1
- Update to 6.34.1.

* Tue Oct 10 2023 Simone Caronni <negativo17@gmail.com> - 6.33.0-1
- Update to 6.33.0.

* Wed Oct 04 2023 Simone Caronni <negativo17@gmail.com> - 6.32.0-1
- Update to 6.32.0.

* Fri Sep 22 2023 Simone Caronni <negativo17@gmail.com> - 6.31.0-1
- Update to 6.31.0.

* Fri Sep 08 2023 Simone Caronni <negativo17@gmail.com> - 6.30.1-1
- Update to 6.30.1.

* Thu Aug 24 2023 Simone Caronni <negativo17@gmail.com> - 6.29.1-1
- Update to 6.29.1.

* Tue Aug 22 2023 Simone Caronni <negativo17@gmail.com> - 6.29.0-1
- Update to 6.29.0.

* Thu Aug 10 2023 Simone Caronni <negativo17@gmail.com> - 6.28.0-1
- Update to 6.28.0.

* Mon Aug 07 2023 Simone Caronni <negativo17@gmail.com> - 6.27.1-1
- Update to 6.27.1.

* Thu Jul 20 2023 Simone Caronni <negativo17@gmail.com> - 6.26.0-1
- Update to 6.26.0.

* Mon Jul 17 2023 Simone Caronni <negativo17@gmail.com> - 6.25.0-1
- Update to 6.25.0.

* Thu Jul 06 2023 Simone Caronni <negativo17@gmail.com> - 6.24.0-1
- Update to 6.24.0.

* Sat Jul 01 2023 Simone Caronni <negativo17@gmail.com> - 6.23.0-1
- Update to 6.23.0.

* Thu Jun 22 2023 Simone Caronni <negativo17@gmail.com> - 6.22.0-1
- Update to 6.22.0.

* Fri Jun 16 2023 Simone Caronni <negativo17@gmail.com> - 6.21.0-1
- Update to 6.21.0.

* Mon Jun 12 2023 Simone Caronni <negativo17@gmail.com> - 6.20.2-1
- Update to 6.20.2.

* Fri Jun 02 2023 Simone Caronni <negativo17@gmail.com> - 6.20.0-1
- Update to 6.20.0.

* Sat May 27 2023 Simone Caronni <negativo17@gmail.com> - 6.19.0-1
- Update to 6.19.0.

* Tue May 23 2023 Simone Caronni <negativo17@gmail.com> - 6.18.1-1
- Update to 6.18.1.

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
