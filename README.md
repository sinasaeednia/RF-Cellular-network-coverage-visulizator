# RF-Cellular-network-coveragae-visulizator
 Visulaize real-time coverage of a RF cellular tower cell

This program extracts the "Cellular OSS output pipeline" and tries to convert it to a visual in Google earth format.
Using this program, the network optimization team, and design team can have a clear view of what happens in the network without dealling with ATOLL and other telecommunication analytical softwares.
The process contains XML parsing using DOM and/or XML templates and storing in SQLite database for better analysis and at the end coverting to XML. 
The professional version of it contains :
	1. Active real-time controls in the Google earth ballon to change the thresholds 
	2. Ability to connect to Snowflake and Azure for further cloud-base data delivery
	3. Ability to refresh to sync to current data and invoke the data from the liive pipeline 

