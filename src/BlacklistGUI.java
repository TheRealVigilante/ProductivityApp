

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

public class BlacklistGUI extends JFrame {
    private JTextArea websitesTextArea;
    private JButton submitButton;
    private final Object lock = new Object();
    private static HashMap<String, WebsiteList> websiteLists = new HashMap<>();
    private String currentListName;

    private void createBlacklist() {
        setTitle("Website Blacklist");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(300, 200);
        setLayout(new BorderLayout());

        websitesTextArea = new JTextArea(10, 20);
        JScrollPane scrollPane = new JScrollPane(websitesTextArea);
        add(scrollPane, BorderLayout.CENTER);

        submitButton = new JButton("Submit");
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String[] websitesArray = websitesTextArea.getText().split("\n");
                ArrayList<String> websitesList = new ArrayList<>();
                for (String website : websitesArray) {
                    websitesList.add(website.trim());
                }
                synchronized (lock) {
                    lock.notify(); // Notify the waiting thread
                }
                // Notify the caller that the list is ready
                onWebsitesListReady(websitesList);
                dispose();
            }
        });
        add(submitButton, BorderLayout.SOUTH);
    }

    private void onWebsitesListReady(ArrayList<String> list) {
        // Process the websitesList here or notify the caller
        System.out.println("Blacklist: " + list);
        WebsiteList websiteList = new WebsiteList(currentListName);
        for (String website : list) {
            websiteList.addWebsite(website);
        }
        websiteLists.put(currentListName, websiteList);
    }
    public static void lockWebsites(String listName) {
        WebsiteList websiteList = websiteLists.get(listName);
        if (websiteList != null) {
            for (String website : websiteList.getWebsites()) {
                website = Website.format(website);
                System.out.println("Locking: " + website);
                Website.blockWebsite(website);
            }
        }
    }
    public void waitForSubmit() {
        synchronized (lock) {
            try {
                lock.wait(); // Wait until the button is clicked
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    public static void unlockWebsites(String listName) throws IOException {
        WebsiteList websiteList = websiteLists.get(listName);
        if (websiteList != null) {
            for (String website : websiteList.getWebsites()) {
                System.out.println("Unlocking: " + website);
                Website.unblockWebsite(website);
            }
        }
    }
    public void launchGUI(String listName) {
        this.currentListName = listName;
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createBlacklist();
                setVisible(true);
            }
        });
    }
}
