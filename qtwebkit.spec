
%define snap 20110603

Name: qtwebkit
Version: 2.2
Release: 5.%{snap}%{?dist}
Summary: Qt WebKit bindings
Group: System Environment/Libraries
License: LGPLv2 with exceptions or GPLv3 with exceptions
URL: http://trac.webkit.org/wiki/QtWebKit
# git archive \
#  --remote git://gitorious.org/+qtwebkit-developers/webkit/qtwebkit.git \
#  --prefix=webkit-qtwebkit/ \
#  qtwebkit-2.2 autogen.sh ChangeLog configure.ac GNUmakefile.am Makefile Source/ Tools/ | xz -9
Source0: webkit-qtwebkit-2.2-%{snap}.tar.xz
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# search /usr/lib{,64}/mozilla/plugins-wrapped for browser plugins too
Patch1: webkit-qtwebkit-2.2-tp1-pluginpath.patch

# type casting
Patch2: webkit-qtwebkit-type-casting.patch

# include JavaScriptCore -debuginfo except on s390(x) during linking of libQtWebKit
Patch3: webkit-qtwebkit-2.2-javascriptcore_debuginfo.patch

# don't use -Werror
Patch4: webkit-qtwebkit-2.2-no_Werror.patch

# fix for qt-4.6.x 
Patch5: webkit-qtwebkit-2.2tp1-qt46.patch

# shared
Patch6: webkit-qtwebkit-2.2-shared.patch

BuildRequires: bison
BuildRequires: chrpath
BuildRequires: flex
BuildRequires: gperf
BuildRequires: libicu-devel
BuildRequires: pcre-devel
BuildRequires: perl
BuildRequires: qt4-devel
# for qtlocation and qtmultimediakit
BuildRequires: qt-mobility-devel >= 1.2
BuildRequires: sqlite-devel

%if 0%{?fedora}
Obsoletes: qt-webkit < 1:4.9.0
Provides: qt-webkit = 2:%{version}-%{release}
Provides: qt4-webkit = 2:%{version}-%{release}
Provides: qt4-webkit%{?_isa} = 2:%{version}-%{release}
%endif

%{?_qt4_version:Requires: qt4%{?_isa} >= %{_qt4_version}}

%description
%{summary}

%package devel
Summary: Development files for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt4-devel
%if 0%{?fedora}
# when qt_webkit_version.pri was moved from qt-devel => qt-webkit-devel
Conflicts: qt-devel < 1:4.7.2-9
Obsoletes: qt-webkit-devel < 1:4.9.0
Provides:  qt-webkit-devel = 2:%{version}-%{release}
Provides:  qt4-webkit-devel = 2:%{version}-%{release}
Provides:  qt4-webkit-devel%{?_isa} = 2:%{version}-%{release}
%endif
%description devel
%{summary}.


%prep
%setup -q -n webkit-qtwebkit 

%patch1 -p1 -b .pluginpath
%patch2 -p1 -b .type-cast
%ifnarch s390
%patch3 -p1 -b .javascriptcore_debuginfo
%endif
%patch4 -p1 -b .no_Werror
%patch5 -p1 -b .qt46
%patch6 -p1 -b .shared

%build 

PATH=%{_qt4_bindir}:$PATH; export PATH
QTDIR=%{_qt4_prefix}; export QTDIR

#  --install-headers=%{_qt4_headerdir} \
#  --install-libs=%{_qt4_libdir} \
Tools/Scripts/build-webkit \
  --makeargs="%{?_smp_mflags}" \
  --qmake=%{_qt4_qmake} \
  --qt \
  --release 

  
%install
rm -rf %{buildroot} 

make install INSTALL_ROOT=%{buildroot} -C WebKitBuild/Release

## HACK, there has to be a better way
chrpath --list   %{buildroot}%{_qt4_libdir}/libQtWebKit.so.4.9.0 ||:
chrpath --delete %{buildroot}%{_qt4_libdir}/libQtWebKit.so.4.9.0 ||:
%if 0%{?_qt4_importdir:1}
chrpath --list   %{buildroot}%{_qt4_importdir}/QtWebKit/libqmlwebkitplugin.so ||:
chrpath --delete %{buildroot}%{_qt4_importdir}/QtWebKit/libqmlwebkitplugin.so ||:
%endif

%clean
rm -rf %{buildroot} 


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%{_qt4_libdir}/libQtWebKit.so.4*
%if 0%{?_qt4_importdir:1}
%{_qt4_importdir}/QtWebKit/
%endif

%files devel
%defattr(-,root,root,-)
%{_qt4_datadir}/mkspecs/modules/qt_webkit_version.pri
%{_qt4_headerdir}/QtWebKit/
%{_qt4_libdir}/libQtWebKit.prl
%{_qt4_libdir}/libQtWebKit.so
%{_libdir}/pkgconfig/QtWebKit.pc


%changelog
* Fri Jun 03 2011 Rex Dieter <rdieter@fedoraproject.org> 2.2-5.20110603
- 20110603 snapshot
- drop unused/deprecated phonon/gstreamer support snippets
- add minimal qt4 dep

* Tue May 24 2011 Than Ngo <than@redhat.com> - 2.2-4.20110513
- fix for qt-4.6.x
- add condition for rhel
- enable shared for qtwebkit build

* Thu May 19 2011 Rex Dieter <rdieter@fedoraproject.org> 2.2-3.20110513
- bump up Obsoletes: qt-webkit a bit, to be on the safe side

* Fri May 13 2011 Rex Dieter <rdieter@fedoraproject.org> 2.2-2.20110513
- 20110513 qtwebkit-2.2 branch snapshot
- cleanup deps
- drop -Werror

* Thu May 12 2011 Than Ngo <than@redhat.com> - 2.2-1
- 2.2-tp1
- gstreamer is now default, drop unneeded phonon patch

* Fri Apr 22 2011 Rex Dieter <rdieter@fedoraproject.org> 2.1-4
- javascriptcore -debuginfo too (#667175)

* Fri Apr 22 2011 Rex Dieter <rdieter@fedoraproject.org> 2.1-3
- Provides: qt(4)-webkit(-devel) = 2:%%version...

* Thu Apr 21 2011 Rex Dieter <rdieter@fedoraproject.org> 2.1-2
- -devel: Conflicts: qt-devel < 1:4.7.2-9 (qt_webkit_version.pri)
- drop old/deprecated Obsoletes/Provides: WebKit-qt
- use modified, less gigantic tarball
- patch to use phonon instead of QtMultimediaKit
- patch pluginpath for /usr/lib{,64}/mozilla/plugins-wrapped

* Tue Apr 19 2011 Rex Dieter <rdieter@fedoraproject.org> 2.1-1
- 2.1

* Mon Nov 08 2010 Than Ngo <than@redhat.com> - 2.0-2
- fix webkit to export symbol correctly

* Tue Nov 02 2010 Rex Dieter <rdieter@fedoraproject.org> 2.0-1
- 2.0 (as released with qt-4.7.0)

* Thu Sep 09 2010 Rex Dieter <rdieter@fedoraproject.org> 2.0-0.1.week32
- first try, borrowing a lot from debian/kubuntu packaging
