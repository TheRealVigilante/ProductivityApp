import java.util.ArrayList;

public class WebsiteList {
    private String name;
    private ArrayList<String> websites;
    private ArrayList<String> applications;

    public WebsiteList(String name) {
        this.name = name;
        this.websites = new ArrayList<>();
        this.applications = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public ArrayList<String> getWebsites() {
        return websites;
    }

    public void addWebsite(String website) {
        this.websites.add(website);
    }
}