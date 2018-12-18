%define major	5
%define libname	%mklibname psl %{major}
%define devname %mklibname psl -d

Name:		libpsl
Summary:	C library for the Public Suffix List
Version:	0.20.2
Release:	1
License:	MIT
Group:		System/Libraries
Url:		https://github.com/rockdaboot/libpsl
Source0:	https://github.com/rockdaboot/libpsl/releases/download/libpsl-%{version}/libpsl-%{version}.tar.gz
BuildRequires:	libicu-devel
BuildRequires:	libidn2-devel
BuildRequires:  publicsuffix-list
# for man-pages
BuildRequires:	xsltproc

%description
A "public suffix" is a domain name under which Internet users can directly
register own names.

Browsers and other web clients can use it to
* avoid privacy-leaking "supercookies"
* avoid privacy-leaking "super domain" certificates
* domain highlighting parts of the domain in a user interface
* sorting domain lists by site

Libpsl:
* has built-in PSL data for fast access (DAWG/DAFSA reduces size from
  180kB to ~32kB)
* allows to load PSL data from files
* checks if a given domain is a "public suffix"
* provides immediate cookie domain verification
* finds the longest public part of a given domain
* finds the shortest private part of a given domain
* works with international domains (UTF-8 and IDNA2008 Punycode)
* is thread-safe
* handles IDNA2008 UTS#46

%package -n psl
Summary:	Commandline utility to explore the Public Suffix List
Group:		Development/Other
Requires:	publicsuffix-list

%description -n psl
This package contains a commandline utility to explore the Public Suffix List,
for example it checks if domains are public suffixes, checks if cookie-domain
is acceptable for domains and so on.

%package -n psl-make-dafsa
Summary:	Compiles the Public Suffix List into DAFSA form
Group:		Development/Other
Requires:	python3

%description -n psl-make-dafsa
This script produces C/C++ code or an architecture-independent binary object
which represents a Deterministic Acyclic Finite State Automaton (DAFSA)
from a plain text Public Suffix List.

%package -n %{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries
Requires:	publicsuffix-list-dafsa

%description -n %{libname}
A "public suffix" is a domain name under which Internet users can directly
register own names.

Browsers and other web clients can use it to
* avoid privacy-leaking "supercookies"
* avoid privacy-leaking "super domain" certificates
* domain highlighting parts of the domain in a user interface
* sorting domain lists by site

Libpsl:
* has built-in PSL data for fast access (DAWG/DAFSA reduces size from
  180kB to ~32kB)
* allows to load PSL data from files
* checks if a given domain is a "public suffix"
* provides immediate cookie domain verification
* finds the longest public part of a given domain
* finds the shortest private part of a given domain
* works with international domains (UTF-8 and IDNA2008 Punycode)
* is thread-safe
* handles IDNA2008 UTS#46

%package -n %{devname}
Summary:	Development files nad headers for %{name}
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Requires:	publicsuffix-list

%description -n %{devname}
This package contains the developmen files and headers for %{name}.

%prep
%autosetup -p1

%build
#
# libicu does allow support for a newer IDN specification (IDN 2008) than
# libidn 1.x (IDN 2003). However, libpsl mostly relies on an internally
# compiled list, which is generated at buildtime and the testsuite thereof
# requires either libidn or libicu only at buildtime; the runtime
# requirement is only for loading external lists, which IIUC neither curl
# nor wget support. libidn2 supports IDN 2008 as well, and is *much* smaller
# than libicu.
#
# curl (as of 7.56.0) now depends on libidn2, and is a core package.
# wget still uses libidn 1.x, but it is not a core package.  Therefore, use
# libidn2 at runtime to help minimize core dependencies.
%configure \
	--disable-static \
	--enable-man \
	--disable-gtk-doc \
	--enable-builtin=libicu \
	--enable-runtime=libidn2 \
	--with-psl-distfile=%{_datadir}/publicsuffix/public_suffix_list.dafsa  \
	--with-psl-file=%{_datadir}/publicsuffix/effective_tld_names.dat       \
	--with-psl-testfile=%{_datadir}/publicsuffix/test_psl.txt

%make_build

%install
%make_install

# the script is noinst but the manpage is installed
install -m0755 src/psl-make-dafsa %{buildroot}%{_bindir}/

# fix shebang
sed -i -e "1s|#!.*|#!%{__python3}|" %{buildroot}%{_bindir}/psl-make-dafsa

#we don't want these
find %{buildroot} -name "*.la" -delete

%check
make check || cat tests/test-suite.log

%files -n psl
%{_bindir}/psl
%{_mandir}/man1/psl.1*

%files -n psl-make-dafsa
%{_bindir}/psl-make-dafsa
%{_mandir}/man1/psl-make-dafsa.1*

%files -n %{libname}
%{_libdir}/libpsl.so.%{major}
%{_libdir}/libpsl.so.%{major}.*

%files -n %{devname}
%{_includedir}/libpsl.h
%{_libdir}/libpsl.so
%{_libdir}/pkgconfig/libpsl.pc
%doc %{_datadir}/gtk-doc/html/%{name}
