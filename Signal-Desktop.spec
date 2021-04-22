# External yarn from https://dl.yarnpkg.com/rpm/
# External nodejs from https://rpm.nodesource.com/pub_12.x/ (requires Python 2)
# Build with --enable-network

%global debug_package %{nil}
#global beta beta.7

# Remove bundled libraries from requirements/provides
%global __requires_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libVkICD_mock_icd\\.so\\..*|libvips\\.so\\..*|libvips-cpp\\.so\\..*|libzkgroup\\.so)$
%global __provides_exclude ^(libffmpeg\\.so.*|libEGL\\.so.*|libGLESv2\\.so.*|libVkICD_mock_icd\\.so\\..*|libvips\\.so\\..*|libvips-cpp\\.so\\..*|libzkgroup\\.so)$

Name:       Signal-Desktop
Version:    5.0.0
Release:    1%{?dist}
Summary:    Private messaging from your desktop
License:    AGPLv3
URL:        https://signal.org/

Source0:    https://github.com/signalapp/%{name}/archive/v%{version}%{?beta:-%{beta}}.tar.gz#/Signal-Desktop-%{version}%{?beta:-%{beta}}.tar.gz
Source2:    %{name}.desktop
Patch0:     %{name}-fix-build.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  git-lfs
%if 0%{?fedora}
BuildRequires:  libxcrypt-compat
%endif
BuildRequires:  nodejs >= 12.13.0
BuildRequires:  openssl-devel
# Python >= 2.6.0 < 3.0.0
BuildRequires:  python2
BuildRequires:  yarn

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

# Allow higher minor node versions
sed -i 's/"node": "/&^/' package.json

%build
yarn install #--verbose
yarn generate --force
# https://github.com/signalapp/Signal-Desktop/issues/2376#issuecomment-457899153
yarn generate exec:build-protobuf exec:transpile concat copy:deps sass
yarn build-release --dir

%install
# Main files
install -dm 755 %{buildroot}%{_libdir}/%{name}
install -dm 755 %{buildroot}%{_bindir}

# Remove unused Chromium components
rm -fr \
  release/linux-unpacked/chrome_*.pak \
  release/linux-unpacked/chrome-sandbox \
  release/linux-unpacked/swiftshader

cp -fr release/linux-unpacked/* %{buildroot}%{_libdir}/%{name}

ln -sf %{_libdir}/%{name}/signal-desktop %{buildroot}%{_bindir}/signal-desktop

# Icons
for size in 16 24 32 48 64 128 256 512 1024; do
  install -p -D -m 644 build/icons/png/${size}x${size}.png \
    %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/%{name}.png
done

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
* Thu Apr 22 2021 Simone Caronni <negativo17@gmail.com> - 5.0.0-1
- Update to 5.0.0.

* Mon Mar 01 2021 Simone Caronni <negativo17@gmail.com> - 1.40.1-1
- Update to 1.40.1.

* Thu Feb 18 2021 Simone Caronni <negativo17@gmail.com> - 1.40.0-4
- Fix typo.

* Thu Feb 18 2021 Simone Caronni <negativo17@gmail.com> - 1.40.0-3
- Update to 1.40.0 final.

* Wed Feb 17 2021 Simone Caronni <negativo17@gmail.com> - 1.40.0-2
- Make sure the correct required glibc version is exposed in the requirements.

* Tue Feb 16 2021 Simone Caronni <negativo17@gmail.com> - 1.40.0-1
- Update to 1.40.0-beta.7.
- Fix license.

* Tue Feb 16 2021 Simone Caronni <negativo17@gmail.com> - 1.39.6-1
- Update to 1.39.6.

* Thu Jan 14 2021 Simone Caronni <negativo17@gmail.com> - 1.39.5-1
- Update to 1.39.5.

* Wed Jan  6 2021 Simone Caronni <negativo17@gmail.com> - 1.39.4-1
- Update to 1.39.4.

* Thu Dec 17 2020 Simone Caronni <negativo17@gmail.com> - 1.39.3-1
- Update to 1.39.3.

* Fri Dec 04 2020 Simone Caronni <negativo17@gmail.com> - 1.38.2-1
- Update to 1.38.2.

* Fri Oct 30 2020 Simone Caronni <negativo17@gmail.com> - 1.37.2-1
- Update to 1.37.2.

* Tue Oct 06 2020 Simone Caronni <negativo17@gmail.com> - 1.36.3-1
- Update to 1.36.3.

* Sun Aug 16 2020 Simone Caronni <negativo17@gmail.com> - 1.34.5-1
- Update to 1.34.5.

* Tue Jul 21 2020 Simone Caronni <negativo17@gmail.com> - 1.34.4-1
- Update to 1.34.4.

* Thu Jul 09 2020 Simone Caronni <negativo17@gmail.com> - 1.34.3-1
- Update to 1.34.3.

* Mon Jun 22 2020 Simone Caronni <negativo17@gmail.com> - 1.34.2-1
- Update to 1.34.2.

* Wed May 20 2020 Simone Caronni <negativo17@gmail.com> - 1.34.1-3
- And now filter out a lot of libraries lying around.

* Wed May 20 2020 Simone Caronni <negativo17@gmail.com> - 1.34.1-2
- Fix 1.34 requiring unpacked app as well.

* Wed May 20 2020 Simone Caronni <negativo17@gmail.com> - 1.34.1-1
- Update to 1.34.1.

* Sat May 02 2020 Simone Caronni <negativo17@gmail.com> - 1.33.4-2
- Do not build unrelated components, fixes build on CentOS/RHEL 7.

* Fri May 01 2020 Simone Caronni <negativo17@gmail.com> - 1.33.4-1
- Update to 1.33.4.

* Fri Apr 24 2020 Simone Caronni <negativo17@gmail.com> - 1.33.3-1
- Update to 1.33.3.

* Tue Apr 14 2020 Simone Caronni <negativo17@gmail.com> - 1.33.0-1
- Update to 1.33.0.

* Thu Mar 26 2020 Matthias Andree <matthias.andree@gmx.de> - 1.32.3-1
- Update to 1.32.3 final.

* Thu Mar 05 2020 Simone Caronni <negativo17@gmail.com> - 1.32.0-4
- Update to 1.32.0 final.

* Tue Mar 03 2020 Simone Caronni <negativo17@gmail.com> - 1.32.0-3
- Update to 1.32.0-beta.5.

* Thu Feb 27 2020 Simone Caronni <negativo17@gmail.com> - 1.32.0-2
- Update to 1.32.0-beta.4.

* Thu Feb 20 2020 Simone Caronni <negativo17@gmail.com> - 1.32.0-1
- Update to 1.32.0 beta 2.

* Wed Feb 12 2020 Simone Caronni <negativo17@gmail.com> - 1.31.0-1
- Update to 1.31.0.

* Thu Feb 06 2020 Simone Caronni <negativo17@gmail.com> - 1.30.1-1
- Update to 1.30.1.
- Use a patched node-sqlcipher 4.x repository (Python, linked OpenSSL).
- Remove unused Electron binaries (sandbox, 3D swiftshader, Electron icons).

* Mon Jan 20 2020 Simone Caronni <negativo17@gmail.com> - 1.29.6-1
- Update to 1.29.6.
- Do not use python-unversioned-command anymore.

* Thu Jan 16 2020 Simone Caronni <negativo17@gmail.com> - 1.29.4-1
- Update to 1.29.4.

* Mon Dec 30 2019 Simone Caronni <negativo17@gmail.com> - 1.29.3-1
- Update to 1.29.3.

* Mon Dec 09 2019 Simone Caronni <negativo17@gmail.com> - 1.29.0-1
- Update to 1.29.0.

* Sat Nov 16 2019 Simone Caronni <negativo17@gmail.com> - 1.28.0-1
- Update to 1.28.0.

* Fri Nov 08 2019 Simone Caronni <negativo17@gmail.com> - 1.27.4-1
- Update to 1.27.4.
- Switch to external yarn/npm stuff.

* Mon Oct 07 2019 Simone Caronni <negativo17@gmail.com> - 1.27.3-1
- Update to 1.27.3.

* Thu Sep 12 2019 Simone Caronni <negativo17@gmail.com> - 1.27.2-1
- Update to 1.27.2.

* Mon Aug 19 2019 Simone Caronni <negativo17@gmail.com> - 1.26.2-1
- Update to 1.26.2.

* Wed Jul 24 2019 Simone Caronni <negativo17@gmail.com> - 1.25.3-2
- First build based on ArchLinux AUR.
