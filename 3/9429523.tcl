#=================================================
#                     Options
#=================================================

set opt(x)		100   
set opt(y)		100   
set opt(nn)		30
set opt(stop)		100
set opt(tr)		9429523.tr
set opt(nam)		9429523.nam
set val(R)              30
#=================================================
#                      MAC
#=================================================

Mac/802_11 set dataRate_        2.0e6
Mac/802_11 set RTSThreshold_    3000

#=================================================
#                     Nodes
#=================================================

set ns_ [new Simulator]
#$ns_ multicast

set tracefd  [open $opt(tr) w]
$ns_ trace-all $tracefd

set namfile [open $opt(nam) w]
$ns_ namtrace-all-wireless $namfile $opt(x) $opt(y)


set topo   [new Topography]
$topo load_flatgrid $opt(x) $opt(y)
create-god  $opt(nn) 

$ns_ node-config -adhocRouting 	AODV \
                 -llType 	LL \
                 -macType 	Mac/802_11 \
                 -ifqType 	Queue/DropTail/PriQueue \
                 -ifqLen 	50 \
                 -antType 	Antenna/OmniAntenna \
		 -propType 	Propagation/FreeSpace \
                 -phyType 	Phy/WirelessPhy \
                 -channelType 	Channel/WirelessChannel \
                 -topoInstance 	$topo \
                 -agentTrace 	ON \
                 -routerTrace 	ON \
                 -macTrace 	OFF \
		 -movementTrace ON


#inital 30 nodes in 100 *100 
for {set i 1} {$i <= $opt(nn)} {incr i} {
    set WT($i) [ $ns_ node $i ]
    set nodeFlag_($i) 0
    $WT($i) random-motion 1
}

for {set i 1} {$i <= $opt(nn)} {incr i} {
   $WT($i) set X_ [expr int($i*rand())]
   $WT($i) set Y_ [expr int($i*rand())]
   $WT($i) set Z_ 0.0

   $ns_ initial_node_pos $WT($i) 2
}


#TS1
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set TS1 $random
	    set $nodeFlag_($random) 1
	    break
}
}

#TR1
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set TR1 $random
	    set $nodeFlag_($random) 1
	    break
}
}

#TS2
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set TS2 $random
	    set $nodeFlag_($random) 1
	    break
}
}

#TR2
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set TR2 $random
	    set $nodeFlag_($random) 1
	    break
}
}

#US
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set US $random

	 #   set outfile [open "report.out" w]
	 #   puts $outfile "$random "
	 #   close $outfile

	    set $nodeFlag_($random) 1
	    break
}
}

#UR
while {1==1} {;
            set random [expr int(30*rand())]
            if {$nodeFlag_($random)==0} {
            set UR $random
	    set $nodeFlag_($random) 1
	    break
}
}

$ns_ at 0 "$WT($TS1) setdest 20 20 3.0"
$ns_ at 10 "$WT($TR1) setdest 24 24 10.0"
$ns_ at 0 "$WT($US) setdest 30 10 5.0"
$ns_ at 50 "$WT($UR) setdest 20 15 3.0"
$ns_ at 0 "$WT($TR2) setdest 27 20 5.0"

#=================================================
#                     Agents
#=================================================
#T1
set T(1) [new Agent/TCP]
$T(1) set class_ 2
$ns_ attach-agent $WT($TS1) $T(1)

set T(2) [new Agent/TCPSink]
$ns_ attach-agent $WT($TR1) $T(2)
$ns_ connect $T(1) $T(2)
$T(1) set fid_ 1

set ftp [new Application/FTP]
$ftp attach-agent $T(1)
$ftp set type_ FTP

$ns_ at 10 "$ftp start"
$ns_ at 60 "$ftp stop"
#U
set U(1) [new Agent/UDP]
$ns_ attach-agent $WT($US) $U(1)

set U(2) [new Agent/Null]
$ns_ attach-agent $WT($UR) $U(2)
$ns_ connect $U(1) $U(2)

set cbr [new Application/Traffic/CBR]
$cbr set packetSize_ 1000
$cbr set interval_ 0.005
$cbr attach-agent $U(1)

$ns_ at 40  "$cbr start"
$ns_ at 80 "$cbr stop"

#T2 -TE
set TE(1) [new Agent/TCP]
$TE(1) set class_ 2
$ns_ attach-agent $WT($TS2) $TE(1)

set TE(2) [new Agent/TCPSink]
$ns_ attach-agent $WT($TR2) $TE(2)
$ns_ connect $TE(1) $TE(2)
$TE(1) set fid_ 1

set Telnet [new Application/Telnet]
#$ftp set rate_ 20kbs
$Telnet set packetSize_ 268
$Telnet attach-agent $TE(1)

$ns_ at 40 "$ftp start"
$ns_ at 70 "$ftp stop"

#=================================================
#                     End
#=================================================
for {set i } {$i <= $opt(nn) } {incr i} {
    $ns_ at $opt(stop).0000010 "$WT($i) reset";
}

$ns_ at $opt(stop).1 "finish"
$ns_ at $opt(stop).2 "$ns_ halt"

proc finish {} {
    global ns_ namfile opt
    $ns_ flush-trace
    close $namfile
    exec nam $opt(nam) &
    exit 0
}

puts "Starting Simulation..."
$ns_ run
