default:
	@echo "Usage:"
	@echo "  make grg"
	@echo "  make open"
	@echo "  make clean"
	@echo "  make reload"

reload:
	unbound-control reload

clean:
	rm plf_zones_*

open: plf_zones_del
	unbound-control local_zones_remove < $>

grg: plf_zones_add
	unbound-control local_zones < $>

plf_zones_add: ../etc/plf_zones
	awk 'BEGIN {print ". refuse";} $$1 !~ /^#/ {printf "%s transparent\n", $$0}' $> > $@

plf_zones_del: ../etc/plf_zones
	awk 'BEGIN {print ".";} $$1 !~ /^#/ {print}' $> > $@


