BEGIN{
	sim_end = 200;
	i=0;
	while (i<=sim_end) {sec[i]=0; i+=1;};
}

{
	if ($1=="s" && ($7=="cbr" || $7=="tcp" $7=="udp" ) && ($3=="_22_"  ||  $3=="_23_") ) {
		sec[int($2)]+=$8;
	};
}

END{	
	i=0;
	while (i<=sim_end) {print i " " sec[i]; i+=1;};
} 
