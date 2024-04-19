import java.util.ArrayList;

public class AppList {
    private String name;
    private ArrayList<String> applications;

    public AppList(String name) {
        this.name = name;
        this.applications = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public ArrayList<String> getApplications() {
        return applications;
    }

    public void addApp(String app) {
        this.applications.add(app);
    }
}