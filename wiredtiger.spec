# FIXME: proper dir for arch-dependent java library, enable java by default
#
# Conditional build:
%bcond_without	static_libs	# static libraries
%bcond_with	java		# Java binding (invalid directory)
%bcond_without	python		# Python binding
#
%{?use_default_jdk:%use_default_jdk}
Summary:	The WiredTiger Data Engine
Summary(pl.UTF-8):	Silnik danych WiredTiger
Name:		wiredtiger
# 1.6.3 is the last version without hard sizeof(void*)==8 assumption
Version:	1.6.3
Release:	1
License:	GPL v2 or GPL v3
Group:		Libraries
#Source0Download: https://github.com/wiredtiger/wiredtiger/releases
Source0:	https://github.com/wiredtiger/wiredtiger/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	fa0e475ab6808adbadc8868078dc94a3
Patch0:		%{name}-python.patch
Patch1:		%{name}-pc.patch
URL:		https://source.wiredtiger.com/
BuildRequires:	autoconf >= 2.63
BuildRequires:	automake >= 1:1.10
BuildRequires:	bzip2-devel
BuildRequires:	libstdc++-devel >= 6:7
BuildRequires:	libtool >= 2:2.2.6
BuildRequires:	rpmbuild(macros) >= 2.022
BuildRequires:	snappy-devel
%if %{with java}
%{?buildrequires_jdk}
BuildRequires:	rpm-javaprov
BuildRequires:	swig >= 2.0.4
%endif
%if %{with python3}
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	python3-setuptools
BuildRequires:	rpm-pythonprov
BuildRequires:	swig-python >= 2.0.4
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
WiredTiger is an high performance, scalable, production quality,
NoSQL, Open Source extensible platform for data management.

%description -l pl.UTF-8
WiredTiger to wysoko wydajna, skalowalna, mająca produkcyjną jakość
i otwarte źródła, rozszerzalna platforma NoSQL do zarządzania danymi.

%package devel
Summary:	Header files for WiredTiger library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki WiredTiger
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for WiredTiger library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki WiredTiger.

%package static
Summary:	Static WiredTiger library
Summary(pl.UTF-8):	Statyczna biblioteka WiredTiger
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static WiredTiger library.

%description static -l pl.UTF-8
Statyczna biblioteka WiredTiger.

%package -n java-wiredtiger
Summary:	Java interface to WiredTiger data engine
Summary(pl.UTF-8):	Interfejs Javy do silnika danych WiredTiger
Group:		Libraries/Java
Requires:	%{name} = %{version}-%{release}

%description -n java-wiredtiger
Java interface to WiredTiger data engine.

%description -n java-wiredtiger -l pl.UTF-8
Interfejs Javy do silnika danych WiredTiger.

%package -n python3-wiredtiger
Summary:	Python interface to WiredTiger data engine
Summary(pl.UTF-8):	Interfejs Pythona do silnika danych WiredTiger
Group:		Libraries/Python
Requires:	%{name} = %{version}-%{release}

%description -n python3-wiredtiger
Python interface to WiredTiger data engine.

%description -n python3-wiredtiger -l pl.UTF-8
Interfejs Pythona do silnika danych WiredTiger.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
# does much more beside autoreconf
./autogen.sh

# requires 64-bit off_t
CPPFLAGS="%{rpmcppflags} $(getconf LFS_CFLAGS)"
%configure \
	PYTHON=%{__python3} \
	--enable-bzip2 \
	--enable-java \
	--enable-python \
	--enable-snappy \
	%{!?with_static_libs:--disable-static}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/libwiredtiger*.la
%if %{with static_libs}
# loadable module
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libwiredtiger_{bzip2,snappy}.a
%endif
%if %{with java}
%{__rm} $RPM_BUILD_ROOT%{_datadir}/java/wiredtiger-%{version}/libwiredtiger_java.la
%if %{with static_libs}
%{__rm} $RPM_BUILD_ROOT%{_datadir}/java/wiredtiger-%{version}/libwiredtiger_java.a
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE NEWS README
%attr(755,root,root) %{_bindir}/wt
%{_libdir}/libwiredtiger-%{version}.so
%{_libdir}/libwiredtiger_bzip2.so
%{_libdir}/libwiredtiger_snappy.so

%files devel
%defattr(644,root,root,755)
%{_libdir}/libwiredtiger.so
%{_includedir}/wiredtiger.h
%{_includedir}/wiredtiger_ext.h
%{_pkgconfigdir}/wiredtiger.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libwiredtiger.a
%endif

%if %{with java}
%files -n java-wiredtiger
%defattr(644,root,root,755)
%dir %{_datadir}/java/wiredtiger-%{version}
%{_datadir}/java/wiredtiger-%{version}/libwiredtiger_java.so*
%{_datadir}/java/wiredtiger-%{version}/wiredtiger.jar
%endif

%if %{with python}
%files -n python3-wiredtiger
%defattr(644,root,root,755)
%{py3_sitedir}/_wiredtiger.cpython-*.so
%{py3_sitedir}/wiredtiger.py
%{py3_sitedir}/__pycache__/wiredtiger.cpython-*.pyc
%{py3_sitedir}/wiredtiger-1.6-py*.egg-info
%endif
