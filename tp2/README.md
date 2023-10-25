# TP2 : Environnement virtuel

Dans ce TP, on remanipule toujours les mêmes concepts qu'au TP1, mais en environnement virtuel avec une posture un peu plus orientée administrateur qu'au TP1.

- [TP2 : Environnement virtuel](#tp2--environnement-virtuel)
- [0. Prérequis](#0-prérequis)
- [I. Topologie réseau](#i-topologie-réseau)
  - [Topologie](#topologie)
  - [Tableau d'adressage](#tableau-dadressage)
  - [Hints](#hints)
  - [Marche à suivre recommandée](#marche-à-suivre-recommandée)
  - [Compte-rendu](#compte-rendu)
- [II. Interlude accès internet](#ii-interlude-accès-internet)
- [III. Services réseau](#iii-services-réseau)
  - [1. DHCP](#1-dhcp)
  - [2. Web web web](#2-web-web-web)

# 0. Prérequis

![One IP 2 VM](./img/oneip.jpg)

La même musique que l'an dernier :

- VirtualBox
- Rocky Linux
  - préparez une VM patron, prête à être clonée
  - système à jour (`dnf update`)
  - SELinux désactivé
  - préinstallez quelques paquets, je pense à notamment à :
    - `vim`
    - `bind-utils` pour la commande `dig`
    - `traceroute`
    - `tcpdump` pour faire des captures réseau

La ptite **checklist** que vous respecterez pour chaque VM :

- [ ] carte réseau host-only avec IP statique
- [ ] pas de carte NAT, sauf si demandée
- [ ] connexion SSH fonctionnelle
- [ ] firewall actif
- [ ] SELinux désactivé
- [ ] hostname défini

Je pardonnerai aucun écart de la checklist côté notation. 🧂🧂🧂

> Pour rappel : une carte host-only dans VirtualBox, ça permet de créer un LAN entre votre PC et une ou plusieurs VMs. La carte NAT de VirtualBox elle, permet de donner internet à une VM.

# I. Topologie réseau

Vous allez dans cette première partie préparer toutes les VMs et vous assurez que leur connectivité réseau fonctionne bien.

On va donc parler essentiellement IP et routage ici.

## Topologie

![Topologie](./img/topo.png)

## Tableau d'adressage

| Node             | LAN1 `10.1.1.0/24` | LAN2 `10.1.2.0/24` |
| ---------------- | ------------------ | ------------------ |
| `node1.lan1.tp2` | `10.1.1.11`        | x                  |
| `node2.lan1.tp2` | `10.1.1.12`        | x                  |
| `node1.lan2.tp2` | x                  | `10.1.2.11`        |
| `node2.lan2.tp2` | x                  | `10.1.2.12`        |
| `router.tp2`     | `10.1.1.254`       | `10.1.2.254`       |

## Hints

➜ **Sur le `router.tp2`**

Il sera nécessaire d'**activer le routage**. Par défaut Rocky n'agit pas comme un routeur. C'est à dire que par défaut il ignore les paquets qu'il reçoit s'il l'IP de destination n'est pas la sienne. Or, c'est précisément le job d'un routeur.

> Dans notre cas, si `node1.lan1.tp2` ping `node1.lan2.tp2`, le paquet a pour IP source `10.1.1.11` et pour IP de destination `10.1.2.11`. Le paquet passe par le routeur. Le routeur reçoit donc un paquet qui a pour destination `10.1.2.11`, une IP qui n'est pas la sienne. S'il agit comme un routeur, il comprend qu'il doit retransmettre le paquet dans l'autre réseau. Par défaut, la plupart de nos OS ignorent ces paquets, car ils ne sont pas des routeurs.

Pour activer le routage donc, sur une machine Rocky :

```bash
$ firewall-cmd --add-masquerade
$ firewall-cmd --add-masquerade --permanent
$ sysctl -w net.ipv4.ip_forward=1
```

```
[hd0@localhost ~]$ sudo firewall-cmd --add-masquerade --permanent
success
```
```
[hd0@rooter ~]$ sudo sysctl -w net.ipv4.ip_forward=1
net.ipv4.ip_forward = 1
```

---

➜ **Les switches sont les host-only de VirtualBox pour vous**

Vous allez donc avoir besoin de créer deux réseaux host-only. Faites bien attention à connecter vos VMs au bon switch host-only.

---

➜ **Aucune carte NAT**

## Marche à suivre recommandée

Dans l'ordre, je vous recommande de :

**1.** créer les VMs dans VirtualBox (clone du patron)  
**2.** attribuer des IPs statiques à toutes les VMs  
**3.** vous connecter en SSH à toutes les VMs  
**4.** activer le routage sur `router.tp2`  
**5.** vous assurer que les membres de chaque LAN se ping, c'est à dire :

- `node1.lan1.tp2`
  - doit pouvoir ping `node2.lan1.tp2`
  - doit aussi pouvoir ping `router.tp2` (il a deux IPs ce `router.tp2`, `node1.lan1.tp2` ne peut ping que celle qui est dans son réseau : `10.1.1.254`)
- `router.tp2` ping tout le monde
- les membres du LAN2 se ping aussi

**6.** ajouter les routes statiques

- sur les deux machines du LAN1, il faut ajouter une route vers le LAN2
- sur les deux machines du LAN2, il faut ajouter une route vers le LAN1

## Compte-rendu

☀️ Sur **`node1.lan1.tp2`**

- afficher ses cartes réseau

```
[hd0@node1 ~]$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:71:7d:0c brd ff:ff:ff:ff:ff:ff
    inet 10.1.1.11/24 brd 10.1.1.255 scope global noprefixroute enp0s3
       valid_lft forever preferred_lft forever
    inet6 fe80::a00:27ff:fe71:7d0c/64 scope link
       valid_lft forever preferred_lft forever
```

- afficher sa table de routage
```
[hd0@node1 ~]$ ip r s
10.1.1.0/24 dev enp0s3 proto kernel scope link src 10.1.1.11 metric 100
10.1.2.0/24 via 10.1.1.254 dev enp0s3 proto static metric 100
```

- prouvez qu'il peut joindre `node2.lan2.tp2`
```
[hd0@node1 ~]$ ping 10.1.2.12 -c 1
PING 10.1.2.12 (10.1.2.12) 56(84) bytes of data.
64 bytes from 10.1.2.12: icmp_seq=1 ttl=63 time=2.09 ms

--- 10.1.2.12 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 2.091/2.091/2.091/0.000 ms
```

- prouvez avec un `traceroute` que le paquet passe bien par `router.tp2`
```
[hd0@node1 ~]$ traceroute 10.1.2.12
traceroute to 10.1.2.12 (10.1.2.12), 30 hops max, 60 byte packets
 1  10.1.1.254 (10.1.1.254)  1.050 ms  0.887 ms  1.090 ms
 2  10.1.2.12 (10.1.2.12)  2.376 ms !X  2.000 ms !X  1.971 ms !X
```

# II. Interlude accès internet

![No internet](./img/no%20internet.jpg)

**On va donner accès internet à tout le monde.** Le routeur aura un accès internet, et permettra à tout le monde d'y accéder : il sera la passerelle par défaut des membres du LAN1 et des membres du LAN2.

**Ajoutez une carte NAT au routeur pour qu'il ait un accès internet.**

☀️ **Sur `router.tp2`**

- prouvez que vous avez un accès internet (ping d'une IP publique)
```
[hd0@node1 ~]$ ping 1.1.1.1 -c 1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=55 time=14.6 ms

--- 1.1.1.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 14.575/14.575/14.575/0.000 ms
```
- prouvez que vous pouvez résoudre des noms publics (ping d'un nom de domaine public)
```
[hd0@node1 ~]$ ping ynov.com -c 1
PING ynov.com (104.26.11.233) 56(84) bytes of data.
64 bytes from 104.26.11.233 (104.26.11.233): icmp_seq=1 ttl=55 time=13.2 ms

--- ynov.com ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 13.200/13.200/13.200/0.000 ms
```

☀️ **Accès internet LAN1 et LAN2**

- ajoutez une route par défaut sur les deux machines du LAN1
```
[hd0@node1lan1 ~]$ sudo ip route add default via 10.1.1.254 dev enp0s3
```
- ajoutez une route par défaut sur les deux machines du LAN2
```
[hd0@node1lan2 ~]$ sudo ip route add default via 10.1.2.254 dev enp0s3
```
- configurez l'adresse d'un serveur DNS que vos machines peuvent utiliser pour résoudre des noms
```
[hd0@node2lan1 ~]$ cat /etc/sysconfig/network-scripts/ifcfg-enp0s3
DEVICE=enp0s3

BOOTPROTO=static
ONBOOT=yes

IPADDR=10.1.1.12
NETMASK=255.255.255.0

DNS1=1.1.1.1
```
- dans le compte-rendu, mettez-moi que la conf des points précédents sur `node2.lan1.tp2`
- prouvez que `node2.lan1.tp2` a un accès internet :
  - il peut ping une IP publique
  - il peut ping un nom de domaine public
```
[hd0@node2lan1 ~]$ ping ynov.com -c 1
PING ynov.com (104.26.11.233) 56(84) bytes of data.
64 bytes from 104.26.11.233 (104.26.11.233): icmp_seq=1 ttl=55 time=16.0 ms

--- ynov.com ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 16.041/16.041/16.041/0.000 ms
```

# III. Services réseau

**Adresses IP et routage OK, maintenant, il s'agirait d'en faire quelque chose nan ?**

Dans cette partie, on va **monter quelques services orientés réseau** au sein de la topologie, afin de la rendre un peu utile que diable. Des machines qui se `ping` c'est rigolo mais ça sert à rien, des machines qui font des trucs c'est mieux.

## 1. DHCP

☀️ **Sur `dhcp.lan1.tp2`**

- n'oubliez pas de renommer la machine (`node2.lan1.tp2` devient `dhcp.lan1.tp2`)
- changez son adresse IP en `10.1.1.253`
```
[hd0@dhcplan1 ~]$ sudo cat /etc/sysconfig/network-scripts/ifcfg-enp0s3
DEVICE=enp0s3

BOOTPROTO=static
ONBOOT=yes

IPADDR=10.1.1.253
NETMASK=255.255.255.0

DNS1=1.1.1.1

[hd0@dhcplan1 ~]$ sudo nmcli con reload

[hd0@dhcplan1 ~]$ sudo nmcli con up enp0s3
```
- setup du serveur DHCP
  - commande d'installation du paquet
```
[hd0@dhcplan1 ~]$ sudo dnf install dhcp-server
```
  - fichier de conf
```
[hd0@dhcplan1 ~]$ sudo cat /etc/dhcp/dhcpd.conf
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd.conf.example
#   see dhcpd.conf(5) man page


default-lease-time 900;
max-lease-time 10800;
ddns-update-style none;
authoritative;
subnet 10.1.1.0 netmask 255.255.255.0 {
  range 10.1.1.100 10.1.1.200;
  option routers 10.1.1.254;
  option subnet-mask 255.255.255.0;
  option domain-name-servers 8.8.8.8;
}

```
  - service actif
```
[hd0@dhcplan1 ~]$ sudo systemctl status dhcpd
● dhcpd.service - DHCPv4 Server Daemon
     Loaded: loaded (/usr/lib/systemd/system/dhcpd.service; enabled; preset: disabled)
     Active: active (running) since Mon 2023-10-23 00:04:44 CEST; 14s ago
[...]
```

☀️ **Sur `node1.lan1.tp2`**

- demandez une IP au serveur DHCP
```
[hd0@node1lan1 ~]$ sudo cat /etc/sysconfig/network-scripts/ifcfg-enp0s3
DEVICE=enp0s3

BOOTPROTO=dhcp
ONBOOT=yes


DNS1=1.1.1.1

[hd0@node1lan1 ~]$ sudo nmcli con reload
[hd0@node1lan1 ~]$ sudo nmcli con up enp0s3
```
- prouvez que vous avez bien récupéré une IP *via* le DHCP
```
[hd0@node1lan1 ~]$ ip a
[...]
enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:71:7d:0c brd ff:ff:ff:ff:ff:ff
    inet 10.1.1.5/24 brd 10.1.1.255 scope global dynamic noprefixroute enp0s8
       valid_lft 86044sec preferred_lft 86044sec
    inet6 fe80::a00:27ff:fe71:7d0c/64 scope link 
       valid_lft forever preferred_lft forever
```
- prouvez que vous avez bien récupéré l'IP de la passerelle
```
[hd0@node1lan1 ~]$ ip r
default via 10.1.1.254 dev enp0s3 
10.1.1.0/24 dev enp0s3 proto kernel scope link src 10.1.1.5 metric 100 
```
- prouvez que vous pouvez `ping node1.lan2.tp2`

## 2. Web web web

Un petit serveur web ? Pour la route ?

On recycle ici, toujours dans un soucis d'économie de ressources, la machine `node2.lan2.tp2` qui devient `web.lan2.tp2`. On va y monter un serveur Web qui mettra à disposition un site web tout nul.

---

La conf du serveur web :

- ce sera notre vieil ami NGINX
- il écoutera sur le port 80, port standard pour du trafic HTTP
- la racine web doit se trouver dans `/var/www/site_nul/`
  - vous y créerez un fichier `/var/www/site_nul/index.html` avec le contenu de votre choix
- vous ajouterez dans la conf NGINX **un fichier dédié** pour servir le site web nul qui se trouve dans `/var/www/site_nul/`
  - écoute sur le port 80
  - répond au nom `site_nul.tp2`
  - sert le dossier `/var/www/site_nul/`
- n'oubliez pas d'ouvrir le port dans le firewall 🌼

---

☀️ **Sur `web.lan2.tp2`**

- n'oubliez pas de renommer la machine (`node2.lan2.tp2` devient `web.lan2.tp2`)
- setup du service Web
  - installation de NGINX
```
  [hd0@webLan2 ~]$ sudo dnf install nginx
```
  - gestion de la racine web `/var/www/site_nul/`
  - configuration NGINX
  ```
    [hd0@webLan2 nginx]$ cat nginx.conf | grep root
        root         /var/www/site_nul/;
  ```

  - service actif
  ```
      [hd0@webLan2 ~]$ sudo systemctl enable nginx
  Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service → /usr/lib/systemd/system/nginx.service.

  ```
  - ouverture du port firewall
  ```
  [hd0@webLan2 ~]$ sudo firewall-cmd --add-port=80/tcp --permanent
success
[hd0@webLan2 ~]$ sudo firewall-cmd --reload
success

  ```
- prouvez qu'il y a un programme NGINX qui tourne derrière le port 80 de la machine (commande `ss`)
```
[hd0@webLan2 nginx]$ ss -lantp
State                    Recv-Q                   Send-Q                                     Local Address:Port                                       Peer Address:Port                   Process                   
LISTEN                   0                        128                                              0.0.0.0:22                                              0.0.0.0:*                                                
LISTEN                   0                        511                                              0.0.0.0:80                                              0.0.0.0:*                                                
LISTEN                   0                        128                                                 [::]:22                                                 [::]:*                                                
LISTEN                   0                        511      

```
- prouvez que le firewall est bien configuré
```
[hd0@webLan2 nginx]$ sudo firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp0s3
  sources: 
  services: cockpit dhcpv6-client ssh
  ports: 80/tcp
  protocols: 
  forward: yes
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules: 
```
☀️ **Sur `node1.lan1.tp2`**

- éditez le fichier `hosts` pour que `site_nul.tp2` pointe vers l'IP de `web.lan2.tp2`
```
[hd0@node1lan2 ~]$ cat /etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
10.1.2.12   site_nul.tp2

```
- visitez le site nul avec une commande `curl` et en utilisant le nom `site_nul.tp2`
```
[hd0@node1lan2 ~]$ curl site_nul.tp2
Un super site nul !
```

![That's all folks](./img/thatsall.jpg)
