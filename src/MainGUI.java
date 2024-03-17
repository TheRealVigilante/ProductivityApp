
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class MainGUI {

    private JFrame frame;
    private JPanel sidePanel;
    private JPanel contentPanel;

    public MainGUI() {
        // Set up the main frame
        frame = new JFrame("Main Page");
        frame.setSize(960,600); //considering the padding
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setLayout(new BorderLayout());
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);

        // Create and set up the side panel
        sidePanel = createSidePanel();

        frame.add(sidePanel, BorderLayout.WEST);

        // Create and set up the content panel
        contentPanel = new JPanel();
        contentPanel.setLayout(new BorderLayout());

        // Initial content (Home page)
        contentPanel.add(createHomePage(), BorderLayout.CENTER);

        frame.add(contentPanel, BorderLayout.CENTER);

        frame.setVisible(true);
    }

    private JPanel createSidePanel () {
        JPanel panel = new JPanel();
        panel.setPreferredSize(new Dimension(250, frame.getHeight())); // Set width to 250 pixels
        panel.setBackground(Color.DARK_GRAY);
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));


        JButton homeButton = createSideBarButton("Home");
        JButton statisticsButton = createSideBarButton("Statistics");

//        sidePanel.add(Box.createVerticalGlue()); // Add some space at the top
        panel.add(Box.createRigidArea(new Dimension(0, 20)));
        panel.add(homeButton);
        panel.add(statisticsButton);
        panel.add(Box.createVerticalGlue()); // Add some space at the bottom

        return  panel;
    }

    private JButton createSideBarButton(String buttonText) {
//        JButton button = createButton(buttonText);
        JButton button = new JButton(buttonText);
        button.setMaximumSize(new Dimension(249, 30));
        button.setHorizontalAlignment(SwingConstants.LEFT);
//        button.setBorder(new EmptyBorder(0, 0, 30, 0));
        button.setForeground(Color.WHITE);
        button.setBackground(Color.DARK_GRAY);
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Handle button click (you can navigate to different pages here)
                if (buttonText.equals("Home")) {
                    contentPanel.removeAll();
                    contentPanel.add(createHomePage(), BorderLayout.CENTER);
                    contentPanel.revalidate();
                    contentPanel.repaint();
                } else if (buttonText.equals("Statistics")) {
                    // Add code to switch to Statistics page
                    contentPanel.removeAll();
                    contentPanel.revalidate();
                    contentPanel.repaint();
                }
            }
        });

        return  button;
    }

    private JPanel createHomePage() {
        JPanel homePage = new JPanel();
        homePage.setLayout(new FlowLayout()); // Use FlowLayout for horizontal alignment

        int btnHeight = 120;
        int btnWidth = 190;

        JButton createBlockButton = createHomeContentButton("Create Block", btnWidth, btnHeight);
        JButton createDeadlockButton = createHomeContentButton("Create Deadlock", btnWidth, btnHeight);
        JButton editBlocksButton = createHomeContentButton("Edit Blocks", btnWidth, btnHeight);

        createBlockButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Handle button click (you can create and show the CreateBlockGUI here)
                CreateBlockGUI createBlockGUI = new CreateBlockGUI();
            }
        });

        homePage.add(createBlockButton);
        homePage.add(createDeadlockButton);
        homePage.add(editBlocksButton);

        return homePage;
    }

    private JButton createHomeContentButton(String buttonText, int width, int height) {
        JButton button = new JButton(buttonText);
        button.setPreferredSize(new Dimension(width, height));
        button.setMargin(new Insets(10, 10, 10, 10));
        return button;
    }


}




class CreateBlockGUI {

    private JFrame blockFrame;
    private String blockName;
    private String [] BlackList, WhiteList;
    private String [] AppList;

    public CreateBlockGUI () {
        blockFrame = new JFrame("Create Block");
        blockFrame.setSize(new Dimension(400, 390));
        blockFrame.setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE); // Close only this window, not the entire application

        // Create tabs
        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.addTab("Name", createNamePanel());
        tabbedPane.addTab("BlackList", createBlackListPanel());
        tabbedPane.addTab("WhiteList", createWhiteListPanel());
        tabbedPane.addTab("App List", createAppListPanel());
        tabbedPane.addTab("Lock Type", createLockTypePanel());

        blockFrame.getContentPane().add(tabbedPane, BorderLayout.CENTER);

        blockFrame.setLocationRelativeTo(null);
        blockFrame.setVisible(true);

    }

    private JPanel createNamePanel() {
        JPanel namePanel = new JPanel();
        namePanel.setLayout(new BoxLayout(namePanel, BoxLayout.Y_AXIS));
        // Add internal padding to the namePanel
        namePanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));


        // Label and Text Field for entering the block name
        JLabel nameLabel = new JLabel("Enter a name for your block:");
        JTextField nameTextField = new JTextField();
        nameTextField.setMaximumSize(new Dimension(Short.MAX_VALUE, nameTextField.getPreferredSize().height));

        // Note text
        JLabel noteLabel = new JLabel("<html><i>Note: Without entering a name, this Block will not be saved.</i></html>");

        // Button container with FlowLayout for Next and Cancel buttons
        JPanel buttonContainer = new JPanel();
        buttonContainer.setLayout(new FlowLayout());

        // Buttons
        JButton nextButton = new JButton("Next");
        JButton cancelButton = new JButton("Cancel");

        // Action listener for Next button
        nextButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Save the user's input to the blockName variable
                blockName = nameTextField.getText();

                // Move to the BlackList tab
                JTabbedPane parentTabbedPane = (JTabbedPane) namePanel.getParent(); // Assuming a nested structure
                parentTabbedPane.setSelectedIndex(parentTabbedPane.indexOfTab("BlackList"));
                System.out.println(blockName);
            }
        });

        // Action listener for Cancel button
        cancelButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Close the window and delete the object
                blockFrame.dispose();
                // Optionally: Set blockName to null or an empty string if you want to clear the input
                blockName = null;

            }
        });

        // Add buttons to the button container
        buttonContainer.add(cancelButton);
        buttonContainer.add(nextButton);

        // Set the alignment of each component to left
        nameLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        nameTextField.setAlignmentX(Component.LEFT_ALIGNMENT);
        noteLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        buttonContainer.setAlignmentX(Component.LEFT_ALIGNMENT);

        // Add components to the panel
        namePanel.add(nameLabel);
        namePanel.add(nameTextField);
        namePanel.add(Box.createRigidArea(new Dimension(0, 4))); // Add some vertical space
        namePanel.add(noteLabel);
        namePanel.add(Box.createRigidArea(new Dimension(0, 35))); // Add some vertical space
        namePanel.add(buttonContainer); // Add the button container instead of individual buttons

        return namePanel;
    }

    private JPanel createBlackListPanel() {
        JPanel blackListPanel = new JPanel();
        blackListPanel.setLayout(new BoxLayout(blackListPanel, BoxLayout.Y_AXIS));
        blackListPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Label for entering URLs
        JLabel enterUrlLabel = new JLabel("Enter the URLs you would like to blacklist one at a time:");

        // Text field for entering URLs
        JTextField urlTextField = new JTextField();
        urlTextField.setMaximumSize(new Dimension(Short.MAX_VALUE, urlTextField.getPreferredSize().height));

        // Button for adding URLs
        JButton addButton = new JButton("Add");
        addButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Add the entered URL to the BlackList array
                String url = urlTextField.getText();
                // Add code to save 'url' to BlackList array
                System.out.println("Added to BlackList: " + url);
                // Clear the text field for the next input
                urlTextField.setText("");
            }
        });

        // Area to display entered URLs
        JTextArea urlDisplayArea = new JTextArea();
        urlDisplayArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(urlDisplayArea);
        scrollPane.setMaximumSize(new Dimension(Short.MAX_VALUE, 100));

        // Buttons container with FlowLayout for Cancel and Next buttons
        JPanel buttonContainer = new JPanel();
        buttonContainer.setLayout(new FlowLayout());

        // Buttons
        JButton cancelButton = new JButton("Cancel");
        JButton nextButton = new JButton("Next");

        // Action listener for Cancel button
        cancelButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Add code to handle cancel action
                System.out.println("Cancel button clicked");
            }
        });

        // Action listener for Next button
        nextButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Add code to handle next action
                System.out.println("Next button clicked");
            }
        });

        buttonContainer.add(cancelButton);
        buttonContainer.add(nextButton);

        enterUrlLabel.setAlignmentX(Component.LEFT_ALIGNMENT);
        urlTextField.setAlignmentX(Component.LEFT_ALIGNMENT);
        addButton.setAlignmentX(Component.LEFT_ALIGNMENT);
        buttonContainer.setAlignmentX(Component.LEFT_ALIGNMENT);


        // Add components to the panel
        blackListPanel.add(enterUrlLabel);
        blackListPanel.add(urlTextField);
        blackListPanel.add(addButton);
        blackListPanel.add(scrollPane);
        blackListPanel.add(Box.createRigidArea(new Dimension(0, 10))); // Add some vertical space

        blackListPanel.add(buttonContainer);

        return blackListPanel;
    }


    private JPanel createWhiteListPanel() {
        JPanel panel = new JPanel();
        // Add components for the "WhiteList" tab
        return panel;
    }

    private JPanel createAppListPanel() {
        JPanel panel = new JPanel();
        // Add components for the "App List" tab
        return panel;
    }

    private JPanel createLockTypePanel() {
        JPanel panel = new JPanel();
        // Add components for the "Lock Type" tab
        return panel;
    }
}