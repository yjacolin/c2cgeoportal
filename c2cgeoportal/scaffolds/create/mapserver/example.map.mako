# restricted access layer
LAYER
    NAME 'layer_name'
    TYPE POLYGON
    TEMPLATE fooOnlyForWMSGetFeatureInfo # For GetFeatureInfo
    EXTENT 420000 30000 900000 350000
    CONNECTIONTYPE postgis
    PROCESSING "CLOSE_CONNECTION=DEFER" # For performance
    CONNECTION "${mapserver_connection}"
    # Example data for secured layer by restriction area
    DATA "geometrie FROM (SELECT geo.* FROM geodata.table AS geo WHERE ST_Contains((${mapfile_data_subselect} 'layer_name'), ST_SetSRID(geo.geometrie, 21781))) as foo using unique id using srid=21781"
    # Example data for secured layer by role (without any area)
    #DATA "geometrie FROM (SELECT geo.geom as geom FROM geodata.table AS geo WHERE %role_id% IN (${mapfile_data_noarea_subselect} 'layer_name')) as foo USING UNIQUE gid USING srid=21781"
    # Example data for public layer
    #DATA "geometrie FROM (SELECT geo.geom as geom FROM geodata.table AS geo) AS foo USING UNIQUE gid USING srid=21781"
    METADATA
        "wms_title" "layer_name" # For WMS
        "wms_srs" "EPSG:21781" # For WMS

        "wfs_enable_request" "*" # Enable WFS for this layer
        "gml_include_items" "all" # For GetFeatureInfo and WFS GetFeature (QueryBuilder)
        "ows_geom_type" "polygon" # For returning geometries in GetFeatureInfo
        "ows_geometries" "geom" # For returning geometries in GetFeatureInfo

        "wms_metadataurl_href" "http://www.example.com/bar" # For metadata URL
        "wms_metadataurl_format" "text/html" # For metadata URL
        "wms_metadataurl_type" "TC211" # For metadata URL

        ${mapserver_layer_metadata} # For secured layers
    END
    VALIDATION
        ${mapserver_layer_validation} # For secured layers
    END
    STATUS ON
    PROJECTION
      "init=epsg:21781"
    END
    CLASS
        NAME "countries"
        OUTLINECOLOR 0 0 0
    END
END

# raster layer (with a tile index)
LAYER
    NAME 'topo'
    GROUP 'plan'
    TYPE RASTER
    STATUS ON
    PROCESSING "RESAMPLE=AVERAGE"
    TILEINDEX "raster/topo"
    TILEITEM "LOCATION"
    MINSCALEDENOM 25000
END
