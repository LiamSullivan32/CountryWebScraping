import geopandas as gpd
import pandas as pd
from countries import runner
import matplotlib.pyplot as plt
import geoplot as gplt
import geoplot.crs as gcrs


def main():
    countries, country_names, cities = runner()
    countries_df = pd.DataFrame({"country": country_names})
    names = [city.name for city in cities]
    latitudes = [float(city.latitude) for city in cities]
    longitudes = [float(city.longitude) for city in cities]

    # Load the world map GeoDataFrame

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    merged = world.set_index("name").join(countries_df.set_index("country"))
    merged.set_crs(epsg=4326, inplace=True)
    merged["color"] = "grey"  # Default color for all countries
    merged.loc[merged.index.isin(country_names), "color"] = "red"
    """
    merged.explore()
    ax = merged[merged.notna().any(axis=1)].plot(color=merged["color"])
    ax.scatter(latitudes, longitudes, color="blue", label="Cities", s=0.5)
    """
    """
    for x, y, label in zip(
        merged.geometry.centroid.x, merged.geometry.centroid.y, merged.index
    ):
        if label in countries:
            print(x)
            ax.text(x, y, label)
    """
    """
    plt.savefig("map.png", dpi=500)
    """
    red_countries = merged[merged["color"] == "red"]
    grey_countries = merged[merged["color"] == "grey"]

    # Create the base plot with grey countries
    ax = gplt.polyplot(
        grey_countries,
        zorder=-1,
        linewidth=1,
        projection=gcrs.PlateCarree(),
        edgecolor="black",
        facecolor="grey",
        figsize=(12, 12),
    )

    gplt.polyplot(
        red_countries,
        ax=ax,  # Use the same axes for overlay
        zorder=0,
        linewidth=1,
        projection=gcrs.PlateCarree(),
        edgecolor="white",
        facecolor="red",
    )

    plt.savefig("output_filename.png", dpi=300)


if __name__ == "__main__":
    main()
