# TODO:
# -DENABLE_MEMKIND (BR: libmemkind) for NVRAM/SSD caches
# -DENABLE_S3 (BR: aws-sdk-cpp: aws-cpp-sdk-s3-crt, aws-cpp-sdk-core)
# -DENABLE_GCP (BR: google-cloud-cpp: google_cloud_cpp_storage, google_cloud_cpp_common)
# -DENABLE_AZURE (BR: azure-sdk-for-cpp: azure-storage-blobs-cpp, azure-core-cpp)
# libaccel-config?
#
# Conditional build:
%bcond_without	static_libs	# static libraries
%bcond_without	python		# Python binding
%bcond_without	qpl		# IAA compression via libqpl
#
%ifnarch %{x8664}
%undefine	with_qpl
%endif
%{?use_default_jdk:%use_default_jdk}
Summary:	The WiredTiger Data Engine
Summary(pl.UTF-8):	Silnik danych WiredTiger
Name:		wiredtiger
Version:	11.3.1
Release:	1
License:	GPL v2 or GPL v3
Group:		Libraries
#Source0Download: https://github.com/wiredtiger/wiredtiger/releases
Source0:	https://github.com/wiredtiger/wiredtiger/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	41baa8cd5d81a48e29921b3fc2a8d306
Patch0:		%{name}-buildtype.patch
URL:		https://source.wiredtiger.com/
%{?with_qpl:BuildRequires:	accel-config-devel}
BuildRequires:	cmake >= 3.10
BuildRequires:	libsodium-devel
BuildRequires:	libstdc++-devel >= 6:7
BuildRequires:	lz4-devel
%{?with_qpl:BuildRequires:	qpl-devel}
BuildRequires:	rpmbuild(macros) >= 2.022
BuildRequires:	snappy-devel
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
%if %{with python3}
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	python3-setuptools
BuildRequires:	rpm-pythonprov
BuildRequires:	swig-python >= 2.0.4
%endif
BuildArch:	%{x8664} aarch64 loongarch64 ppc64le riscv64 s390x
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

# modules, not executables
%{__sed} -i -e '1s,#!/usr/bin/env python$,#,' lang/python/wiredtiger/*.py

%build
install -d build
cd build
# test/checkpoint/test_checkpoint.c: In function `flcs_decode_value'
# test/checkpoint/test_checkpoint.c:571:35: error: initializer-string for array of `char` truncates NUL terminator but destination lacks `nonstring` attribute (5 chars into 4 available) [-Werror=unterminated-string-initialization]
# test/csuite/config/main.c: In function `handle_wiredtiger_message':
# test/csuite/config/main.c:297:12: error: assignment discards `const' qualifier from pointer target type [-Werror=discarded-qualifiers]
CFLAGS="%{rpmcflags} -Wno-error=unterminated-string-initialization -Wno-error=discarded-qualifiers"
%cmake .. \
	-DCMAKE_INSTALL_INCLUDEDIR=include \
	-DCMAKE_INSTALL_LIBDIR=%{_lib} \
	%{?with_qpl:-DENABLE_IAA=ON} \
	-DENABLE_LZ4=ON \
	-DENABLE_PYTHON=%{__ON_OFF python} \
	-DENABLE_SNAPPY=ON \
	-DENABLE_SODIUM=ON \
	%{?with_static_libs:-DENABLE_STATIC=ON} \
	-DENABLE_ZLIB=ON \
	-DENABLE_ZSTD=ON

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with python}
install -d $RPM_BUILD_ROOT%{py3_sitedir}
install build/lang/python/_wiredtiger.so $RPM_BUILD_ROOT%{py3_sitedir}
cp -pr build/lang/python/wiredtiger $RPM_BUILD_ROOT%{py3_sitedir}
%py3_comp $RPM_BUILD_ROOT%{py3_sitedir}
%py3_ocomp $RPM_BUILD_ROOT%{py3_sitedir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE README
%attr(755,root,root) %{_bindir}/wt
%{_libdir}/libwiredtiger.so.%{version}
%if %{with qpl}
%{_libdir}/libwiredtiger_iaa.so
%endif
%{_libdir}/libwiredtiger_lz4.so
%{_libdir}/libwiredtiger_snappy.so
%{_libdir}/libwiredtiger_sodium.so
%{_libdir}/libwiredtiger_zlib.so
%{_libdir}/libwiredtiger_zstd.so

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

%if %{with python}
%files -n python3-wiredtiger
%defattr(644,root,root,755)
%{py3_sitedir}/_wiredtiger.so
%{py3_sitedir}/wiredtiger
# not created in 11.x
#%{py3_sitedir}/wiredtiger-%{version}-py*.egg-info
%endif
