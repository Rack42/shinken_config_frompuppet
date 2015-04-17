sup_template = { 
'shinken_host':
"""
define host {
	use		{{ template }}
	host_name	{{ name }}
	address		{{ macros['Shinken::Packs::Host']['address'] }}
        aliasname       {% if macros['Shinken::Packs::Host']['aliasname'] %}{{macros['Shinken::Packs::Host']['aliasname']}}{% else %}{{ name }}{% endif %}
	realm		{{ macros['Shinken::Packs::Host']['realm'] }}
        business_impact {{ macros['Shinken::Packs::Host']['business_impact'] }}
        hostgroups      {{ macros['Shinken::Packs::Host']['hostgroup'] }}
{% if macros['Shinken::Packs::Host']['poller_tag'] %}    poller_tag      {{ macros['Shinken::Packs::Host']['poller_tag'] }} {% endif %}

  {%- for pack in macros %}
    {%- if pack != 'Shinken::Packs::Host' %}
      ## Specific variables for : {{ pack }}
      {%- for var in macros[pack] %}
      {%- if macros[pack][var]  %} 
        {% filter upper %}_{{ var }}{% endfilter %} {{ macros[pack][var] }}
      {%- endif %}
      {%- endfor %}
    {%- endif %}
  {% endfor %}

}
"""
,
}

mapping = {
'Shinken::Packs::Common': 'linux',
'Shinken::Packs::Apache': 'apache',
'Shinken::Packs::Nginx': 'nginx',
'Shinken::Packs::Haproxy': 'haproxy',
'Shinken::Packs::Bonding': 'bonding',
'Shinken::Packs::Hardware': 'hardware',
'Shinken::Packs::Mongodb': 'mongodb',
'Shinken::Packs::Postgresql': 'postgresql',
'Shinken::Packs::Mysql': 'mysql',
'Shinken::Packs::Redis': 'redis',
'Shinken::Packs::Puppetmaster': 'puppetmaster',
'Shinken::Packs::Puppetdb': 'puppetdb',
'Shinken::Packs::Bind': 'bind',
'Shinken::Packs::Host': '',
}
