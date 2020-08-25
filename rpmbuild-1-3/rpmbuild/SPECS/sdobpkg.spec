%define debug_package %{nil}
Name:           sdobpkg
Version:        1.3 
Release:        1%{?dist}
Summary:        A see desktop on browser package
 
Group:          Duo
License:        GPL
URL:            https://github.com/Penguin135/Python_Websocket
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  /bin/rm, /bin/mkdir, /bin/cp
Requires:       /bin/bash
 
%description
 A see desktop on browser package
 
%prep
%setup -q
 
 
%build

#configure
#make %{?_smp_mflags}
 
%install
rm -rf $RPM_BUILD_ROOT
#make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/sdob
mkdir -p $RPM_BUILD_ROOT/usr/local/bin
cp sdob-install $RPM_BUILD_ROOT/usr/local/bin
#install -m 755 sdob-install $RPM_BUILD_ROOT/root/bin/sdob-install
cp server.py $RPM_BUILD_ROOT/opt/sdob
cp index.html $RPM_BUILD_ROOT/opt/sdob
cp file.png $RPM_BUILD_ROOT/opt/sdob
cp directory.png $RPM_BUILD_ROOT/opt/sdob
cp sdob-server.service $RPM_BUILD_ROOT/opt/sdob
cp sdob-web.service $RPM_BUILD_ROOT/opt/sdob
cp sdob.target $RPM_BUILD_ROOT/opt/sdob
cp sdob.conf $RPM_BUILD_ROOT/opt/sdob
cp webserver.sh $RPM_BUILD_ROOT/opt/sdob

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
#/root/bin/sdob-install
#%doc

%attr(0755,root,root)/usr/local/bin/sdob-install
%attr(0755,root,root)/opt/sdob/server.py
%attr(-,root,root)/opt/sdob/index.html
%attr(-,root,root)/opt/sdob/file.png
%attr(-,root,root)/opt/sdob/directory.png
%attr(-,root,root)/opt/sdob/sdob-server.service
%attr(-,root,root)/opt/sdob/sdob-web.service
%attr(-,root,root)/opt/sdob/sdob.target
%attr(-,root,root)/opt/sdob/sdob.conf
%attr(-,root,root)/opt/sdob/webserver.sh

%changelog
* Sat Aug 25 2020 Penguin135 <rudwns273@naver.com> - 1.3
- Initial RPM
